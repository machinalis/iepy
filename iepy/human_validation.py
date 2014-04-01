from collections import OrderedDict

from colorama import init as colorama_init, Fore, Style
from future.builtins import input
from termcolor import colored


QUESTION_TEMPLATE = """
Is the following text evidence of the Fact (%(ent_a)s, %(relation)s, %(ent_b)s)?
    %(text)s
(%(keys)s): """


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
    YES = u'y'
    NO = u'n'
    DISCARD = u'd'
    RUN = u'run'
    base_options = OrderedDict(
        [(YES, u'Valid Evidence'),
         (NO, u'Not valid Evidence'),
         (DISCARD, u'Discard, not sure'),
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
        r = u"You'll be presented with pieces of text that have a good chance of be "
        r += u"an evidence of the Fact expressed next. Please confirm or reject each.\n"
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
        fact = evidence.fact
        answer = input(self.template % {
            'keys': keys, 'ent_a': colored(fact.e1.key, 'red'),
            'ent_b': colored(fact.e2.key, 'green'), 'relation': fact.relation,
            'text': self.format_segment_text(evidence, Fore.RED, Fore.GREEN)
        })
        while answer not in self.keys:
            answer = input('Invalid answer. (%s): ' % keys)
        return answer

    def format_segment_text(self, evidence, color_1, color_2):
        """Will return a naive formated text with entities remarked.
        Assumes that occurrences does not overlap.
        """
        sgm = evidence.segment
        occurr1 = sgm.entities[evidence.o1]
        occurr2 = sgm.entities[evidence.o2]
        tkns = sgm.tokens[:]
        if evidence.o1 < evidence.o2:
            tkns.insert(occurr2.offset_end, Style.RESET_ALL)
            tkns.insert(occurr2.offset, color_2)
            tkns.insert(occurr1.offset_end, Style.RESET_ALL)
            tkns.insert(occurr1.offset, color_1)
        else:  # must be solved in the reverse order
            tkns.insert(occurr1.offset_end, Style.RESET_ALL)
            tkns.insert(occurr1.offset, color_1)
            tkns.insert(occurr2.offset_end, Style.RESET_ALL)
            tkns.insert(occurr2.offset, color_2)
        return u' '.join(tkns)
