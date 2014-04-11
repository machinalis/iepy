from unittest import TestCase
try:
    from unittest import mock
except ImportError:
    import mock

import colorama

from iepy.human_validation import TerminalInterviewer
from .factories import EntityFactory, EvidenceFactory


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
        fmtted = ev.colored_text(self.c1, self.c2)
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
        fmtted = ev.colored_text(self.c1, self.c2)
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
        fmtted = ev.colored_text(self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Tom', self.reset, u'hates not Sarah but',
                       self.c2, u'Peter Parker', self.reset, u'.']))


class HumanValidationTests(TestCase):

    def setUp(self):
        patcher = mock.patch.object(TerminalInterviewer, 'get_human_answer')
        self.mock_get_answer = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(TerminalInterviewer, 'explain')
        self.mock_explain = patcher.start()
        self.addCleanup(patcher.stop)

    def create_question(self, e1, e2, text, confidence=0.5):
        """Simplistic question creator. It's going to create something that will match
        data types, and just that.
        Probably internal offsets will not be good, but will not cause exceptions.
        Text shall not contain the keys for e1 and e2 (meaning it's not checked), but
        shall have at least 4 tokens.
        """
        e1 = EntityFactory(key=e1)
        e2 = EntityFactory(key=e2)
        tokens = text.split()
        ev = EvidenceFactory(
            fact__e1=e1, fact__e2=e2,
            occurrences__data=[(e1, 0, 1), (e2, 1, 2)],
            segment__tokens=tokens)
        return ev, confidence

    def test_questions_are_consulted_in_given_order(self):
        q1 = self.create_question(u'Tom', u'Pizza', 'Tom eats Pizza happily .')
        q2 = self.create_question(u'Tom', u'Cheese', 'Tom eats Cheese happily .')
        self.term = TerminalInterviewer([q1, q2], mock.MagicMock())
        self.term()
        self.assertEqual(self.mock_get_answer.call_count, 2)
        self.assertEqual(
            self.mock_get_answer.call_args_list,
            [mock.call(q1[0]), mock.call(q2[0])])

    def test_YES_NO_answers_are_passed_with_callback_and_proceeds(self):
        q1 = self.create_question(u'Tom', u'Pizza', 'Tom eats Pizza happily .')
        q2 = self.create_question(u'Tom', u'Cheese', 'Tom eats Cheese happily .')
        callback = mock.MagicMock()
        self.term = TerminalInterviewer([q1, q2], callback)
        self.mock_get_answer.side_effect = [self.term.YES, self.term.NO]
        result = self.term()
        self.assertIsNone(result)
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(
            callback.call_args_list,
            [mock.call(q1[0], True), mock.call(q2[0], False)])

    def test_user_can_say_he_is_tired_and_no_more_questions_are_shown(self):
        q1 = self.create_question(u'Tom', u'Pizza', 'Tom eats Pizza happily .')
        q2 = self.create_question(u'Tom', u'Cheese', 'Tom eats Cheese happily .')
        self.term = TerminalInterviewer([q1, q2], mock.MagicMock())
        self.mock_get_answer.side_effect = [self.term.RUN, self.term.YES]
        result = self.term()
        # after user says is tired, no more questions
        self.assertEqual(self.mock_get_answer.call_count, 1)
        self.assertIsNone(result)

    def test_user_is_confused_then_callback_is_not_invoken_but_next_question_goes(self):
        q1 = self.create_question(u'Tom', u'Cheese', 'Tom Cheese happily eats.')
        q2 = self.create_question(u'Tom', u'Pizza', 'Tom eats Pizza happily .')
        q3 = self.create_question(u'Tom', u'Cheese', 'Tom eats Cheese happily .')
        callback = mock.MagicMock()
        self.term = TerminalInterviewer([q1, q2, q3], callback)
        self.mock_get_answer.side_effect = [self.term.DISCARD, self.term.YES,
                                            self.term.YES]
        result = self.term()
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(
            callback.call_args_list,
            [mock.call(q2[0], True), mock.call(q3[0], True)])
        self.assertEqual(self.mock_get_answer.call_count, 3)
        self.assertIsNone(result)

    def test_custom_options_stop_execution_and_are_returned(self):
        CUSTOM = u'custom'
        q1 = self.create_question(u'Tom', u'Pizza', 'Tom eats Pizza happily .')
        q2 = self.create_question(u'Tom', u'Cheese', 'Tom eats Cheese happily .')
        self.term = TerminalInterviewer(
            [q1, q2], mock.MagicMock(),
            extra_options=[(CUSTOM, u'some explanation')])
        self.mock_get_answer.side_effect = [CUSTOM, self.term.YES]
        result = self.term()
        # after user picks custom option, no more questions, and returned option
        self.assertEqual(self.mock_get_answer.call_count, 1)
        self.assertEqual(result, CUSTOM)
