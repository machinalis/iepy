from collections import OrderedDict

from colorama import init as colorama_init
from future.builtins import input, str

from iepy.pycompatibility import PY2


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

    def explain(self):
        """Returns string that explains how to use the tool for the person
        answering questions.
        """
        r = u"You'll be presented with pieces of text that have a good chance to be "
        r += u"evidences of the seed facts. Please confirm or reject each.\n"
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
        for evidence, score in self.questions[len(self.raw_answers):]:
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
        c_fact, c_text = evidence.colored_fact_and_text()
        question = self.template % {
            'keys': keys, 'fact': c_fact,
            'text': c_text
        }
        if PY2:
            question = question.encode('utf-8')
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
