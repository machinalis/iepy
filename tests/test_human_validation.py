from contextlib import contextmanager
from io import StringIO
import sys
from unittest import TestCase

import colorama

from iepy.human_validation import TerminalInterviewer
from .factories import EntityFactory, EvidenceFactory


@contextmanager
def capture(command, *args, **kwargs):
    out, sys.stdout = sys.stdout, StringIO()
    command(*args, **kwargs)
    sys.stdout.seek(0)
    yield sys.stdout.read()
    sys.stdout = out


class HumanValidationTests(TestCase):

    def test_x(self):
        pass


class TextSegmentFormatting(TestCase):

    def setUp(self):
        self.c1 = colorama.Fore.GREEN
        self.c2 = colorama.Fore.RED
        self.reset = colorama.Style.RESET_ALL
        self.term = TerminalInterviewer([], lambda x: x)

    def test_colorized_simple(self):
        e1 = EntityFactory(key=u'Peter')
        e2 = EntityFactory(key=u'Sarah')
        tokens = [u'Peter', u'likes', u'Sarah', u'.']
        ev = EvidenceFactory(
            fact__e1=e1, fact__e2=e2,
            occurrences__data=[(e1, 0, 1), (e2, 2, 3)],
            segment__tokens=tokens)
        fmtted = self.term.format_segment_text(ev, self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Peter', self.reset, u'likes',
                       self.c2, u'Sarah', self.reset, u'.']))

    def test_colorized_larger(self):
        e1 = EntityFactory(key=u'Peter')
        e2 = EntityFactory(key=u'Sarah Jessica Parker')
        tokens = [u'Peter', u'likes', u'Sarah', u'Jessica', u'Parker', u'.']
        ev = EvidenceFactory(
            fact__e1=e1, fact__e2=e2,
            occurrences__data=[(e1, 0, 1), (e2, 2, 5)],
            segment__tokens=tokens)
        fmtted = self.term.format_segment_text(ev, self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Peter', self.reset, u'likes',
                       self.c2, u'Sarah', u'Jessica', u'Parker', self.reset, u'.']))

    def test_colorize_when_several_more_occurrences(self):
        e1 = EntityFactory(key=u'Tom')
        e2 = EntityFactory(key=u'Sarah')
        e3 = EntityFactory(key=u'Peter Parker')
        tokens = [u'Tom', u'hates', u'not', u'Sarah', u'but', u'Peter', u'Parker', u'.']
        ev = EvidenceFactory(
            fact__e1=e1, fact__e2=e2, fact__relation='hates',
            occurrences__data=[(e1, 0, 1), (e2, 3, 4), (e3, 5, 7)],
            o1=0, o2=2, segment__tokens=tokens)
        fmtted = self.term.format_segment_text(ev, self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Tom', self.reset, u'hates not Sarah but',
                       self.c2, u'Peter Parker', self.reset, u'.']))
