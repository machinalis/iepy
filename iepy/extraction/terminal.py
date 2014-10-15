from collections import OrderedDict
import logging

from colorama import Fore, Style, init as colorama_init
from future.builtins import input, str

from iepy.data.db import CandidateEvidenceManager
from iepy.data.models import SegmentToTag


logger = logging.getLogger(__name__)


class Answers(object):
    YES = u'y'
    NO = u'n'
    DONT_KNOW = u'd'
    STOP = u'stop'
    options = [YES, NO, DONT_KNOW, STOP]
    values = {YES: 1.0, NO: 0.0, DONT_KNOW: 0.5}


QUESTION_TEMPLATE = str(u"""
Is the following text evidence of the Fact %(fact)s?
    %(text)s
(%(keys)s): """)


class TerminalInterviewer(object):
    """
    Capable of asking Human to validate evidence for some facts over a text terminal.
    Questions is a list of tuples of (Evidence, score), that will be consumed in
    the received order.
    Each time an evidence is validated or rejected by the human, correspondent
    boolean answer is stored by calling the provided callback.
    Extra options can be defined (key, explanation) like this:
        extra_options=[('stop', 'Stop algorithm')]
    when user picks such answers, the control is returned to the caller,
    leaving the internal state untouched, so it's possible to resume execution.
    """
    # FIXME: this "options" shall be merged with the Answers class defined above.
    YES = u'y'
    NO = u'n'
    DONT_KNOW = u'd'
    RUN = u'run'
    base_options = OrderedDict(
        [(YES, u'Valid Evidence'),
         (NO, u'Not valid Evidence'),
         (DONT_KNOW, u'Discard, not sure'),
         (RUN, u'Tired of answering for now. Run with what I gave you.')
         ])
    template = QUESTION_TEMPLATE

    def __init__(self, questions, store_answer_callback,
                 extra_options=None):
        """
        Creates an object capable of asking Human to validate evidence for some facts.
        Questions is a list of tuples of (Evidence, score), that will be consumed in
        the received order.
        Each time an evidence is validated or rejected by the human, correspondent
        boolean answer is stored by calling the provided callback.
        Extra options can be defined (key, explanation) like this:
            extra_options=[('stop', 'Stop algorithm')]
        when user use such answers, flow is returned to the caller,
        and question is discarded (so it's possible to resume execution)
        """
        self.questions = questions
        self.raw_answers = []  # list of answers
        self.store_answer_callback = store_answer_callback
        self.extra_options = OrderedDict(extra_options or [])
        if set(self.base_options).intersection(self.extra_options.keys()):
            raise ValueError(u"Can't define extra answers with the builtin keys")
        self.keys = list(self.base_options.keys()) + list(self.extra_options.keys())
        self.formatter = TerminalEvidenceFormatter()

    def explain(self):
        """Returns string that explains how to use the tool for the person
        answering questions.
        """
        r = u"You'll be presented with pieces of text that have a good chance to be "
        r += u"evidences of the known facts. Please confirm or reject each.\n"
        r += u"Pay attention to the colors.\n"
        r += u"Possible answers are:\n"
        options = list(self.base_options.items()) + list(self.extra_options.items())
        r += u'\n'.join('   %s: %s' % (key, explanation) for key, explanation in options)
        print(r)

    def __call__(self):
        """For each available question prompts the Human if it's valid evidence or not.

        Returns None in case that all question has been answered (or when the Human
        indicates that he's tired of answering).
        Each time that Human replies with a custom answer (not in the base list) that
        answer will be returned instantaneously (and no further question will be shown
        except the terminal is invoked again).
        """
        colorama_init()
        self.explain()
        for evidence in self.questions[len(self.raw_answers):]:
            answer = self.get_human_answer(evidence)
            if answer in self.extra_options:
                # Will not be handled here but in the caller.
                return answer
            elif answer == self.RUN:
                # No more questions and answers for now. Use what is available.
                return None
            else:
                self.raw_answers.append(answer)
                if answer in [self.YES, self.NO]:
                    self.store_answer_callback(evidence, answer == self.YES)

    def get_human_answer(self, evidence):
        keys = u'/'.join(self.keys)
        c_fact, c_text = self.formatter.colored_fact_and_text(evidence)
        question = self.template % {
            'keys': keys, 'fact': c_fact,
            'text': c_text
        }
        answer = input(question)
        while answer not in self.keys:
            answer = input('Invalid answer. (%s): ' % keys)
        return answer


def human_oracle(evidence, possible_answers):
    """Simple text interface to query a human for fact generation."""
    colored_fact, colored_segment = evidence.colored_fact_and_text()
    print(u'SEGMENT: %s' % colored_segment)
    question = ' FACT: {0}? ({1}) '.format(colored_fact,
                                           u'/'.join(possible_answers))
    answer = input(question)
    while answer not in possible_answers:
        answer = input(question)
    return answer


class TerminalEvidenceFormatter(object):
    default_color_1 = Fore.RED
    default_color_2 = Fore.GREEN

    def colored_text(self, ev, color_1=None, color_2=None):
        """Will return a naive formated text with entities remarked.
        Assumes that occurrences does not overlap.
        """
        color_1 = color_1 or self.default_color_1
        color_2 = color_2 or self.default_color_2

        # right and left entity-occurrences. "Right" and "Left" are just ideas, but
        # are not necessary their true position on the text
        r_eo = ev.right_entity_occurrence
        l_eo = ev.left_entity_occurrence
        ev.segment.hydrate()
        r_eo.hydrate_for_segment(ev.segment)
        l_eo.hydrate_for_segment(ev.segment)
        tkns = ev.segment.tokens[:]
        if r_eo.segment_offset < l_eo.segment_offset:
            tkns.insert(l_eo.segment_offset_end, Style.RESET_ALL)
            tkns.insert(l_eo.segment_offset, color_2)
            tkns.insert(r_eo.segment_offset_end, Style.RESET_ALL)
            tkns.insert(r_eo.segment_offset, color_1)
        else:  # must be solved in the reverse order
            tkns.insert(r_eo.segment_offset_end, Style.RESET_ALL)
            tkns.insert(r_eo.segment_offset, color_1)
            tkns.insert(l_eo.segment_offset_end, Style.RESET_ALL)
            tkns.insert(l_eo.segment_offset, color_2)
        return u' '.join(tkns)

    def colored_fact(self, ev, color_1=None, color_2=None):
        color_1 = color_1 or self.default_color_1
        color_2 = color_2 or self.default_color_2
        right_entity = ev.right_entity_occurrence.entity
        left_entity = ev.left_entity_occurrence.entity
        return u'(%s <%s>, %s, %s <%s>)' % (
            color_1 + right_entity.key + Style.RESET_ALL,
            right_entity.kind,
            ev.relation.name,
            color_2 + left_entity.key + Style.RESET_ALL,
            left_entity.kind,
        )

    def colored_fact_and_text(self, ev, color_1=None, color_2=None):
        color_1 = color_1 or self.default_color_1
        color_2 = color_2 or self.default_color_2

        return (
            self.colored_fact(ev, color_1, color_2),
            self.colored_text(ev, color_1, color_2)
        )


class TerminalAdministration(object):
    """Terminal/Console interface for administrating the run of a iepy extraction.
    """
    REFRESH = u'refresh'
    RUN = u'run'
    base_options = OrderedDict(
        [(REFRESH, u'Refresh - check how many new labels were created.'),
         (RUN, u'Run Process - run the process again with the info obtained'),
         ])

    def __init__(self, relation, extra_options):
        self.relation = relation
        self.extra_options = OrderedDict(extra_options or [])
        if set(self.base_options).intersection(self.extra_options.keys()):
            raise ValueError(u"Can't define extra options with the builtin keys")
        self.keys = list(self.base_options.keys()) + list(self.extra_options.keys())

    def update_candidate_evidences_to_label(self, evidence_candidates):
        # Will let the UI know which are the segments that have evidence to label.
        # Needs to respect the provided ordering, so the created SegmentToTag objects
        # when sorted by date respect the evidence_candidates provided.
        logger.info('Creating segments to tag')
        segments_to_tag = []
        for ev_c in evidence_candidates:
            if ev_c.segment not in segments_to_tag:
                segments_to_tag.append(ev_c.segment)

        existent_stt = {stt.segment_id: stt for stt in SegmentToTag.objects.filter(
            relation=self.relation, segment__in=segments_to_tag)}
        for segment in segments_to_tag:
            if segment.pk in existent_stt:
                stt = existent_stt[segment.pk]
            else:
                stt, created = SegmentToTag.objects.get_or_create(
                    segment=segment,
                    relation=self.relation,
                )
            if not stt.done:
                stt.save()  # always saving, so modification_date is updated
        logger.info('Done creating segments to tag')

    def explain(self):
        """Returns string that explains how to use the tool for the person
        administering the extraction.
        """
        r = "Waiting for candidate evidences to be labeled. \n"
        r += "Available commands are:\n"
        options = list(self.base_options.items()) + list(self.extra_options.items())
        r += u'\n'.join('   %s: %s' % (key, explanation) for key, explanation in options)
        print(r)

    def __call__(self):
        self.explain()
        while True:
            # Forever loop until the administrator decides to stop it
            cmd = self.get_command()
            if cmd in self.extra_options or cmd == self.RUN:
                return cmd
            if cmd == self.REFRESH:
                self.refresh_info()

    def refresh_info(self):
        c = CandidateEvidenceManager.value_labeled_candidates_count_for_relation(
            self.relation)
        print ('There are %s labels with yes/no answers' % c)

    def get_command(self):
        keys = u'/'.join(self.keys)
        answer = input('Waiting... what to do: ')
        while answer not in self.keys:
            answer = input('"%s" is an invalid answer. (%s): ' % (answer, keys))
        return answer
