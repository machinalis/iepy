from unittest import mock

import colorama

from iepy.extraction.terminal import TerminalInterviewer, TerminalEvidenceFormatter
from .factories import EvidenceFactory
from .manager_case import ManagerTestCase


class TextSegmentFormatting(ManagerTestCase):

    def setUp(self):
        self.c1 = colorama.Fore.GREEN
        self.c2 = colorama.Fore.RED
        self.reset = colorama.Style.RESET_ALL
        self.term = TerminalInterviewer([], lambda x: x)
        self.formatter = TerminalEvidenceFormatter()

    def test_colorized_simple(self):
        ev = EvidenceFactory(markup="{Peter|Person*} likes {Sarah|Person**} .")
        fmtted = self.formatter.colored_text(ev, self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Peter', self.reset, u'likes',
                       self.c2, u'Sarah', self.reset, u'.']))

    def test_colorized_larger(self):
        ev = EvidenceFactory(markup="{Peter|Person*} likes {Sarah Jessica Parker|Person**} .")
        fmtted = self.formatter.colored_text(ev, self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Peter', self.reset, u'likes',
                       self.c2, u'Sarah', u'Jessica', u'Parker', self.reset, u'.']))

    def test_colorize_when_several_more_occurrences(self):
        ev = EvidenceFactory(markup="{Tom|Person*} hates not {Sarah|Person} but {Peter Parker|Person**} .")
        fmtted = self.formatter.colored_text(ev, self.c1, self.c2)
        self.assertEqual(
            fmtted,
            u' '.join([self.c1, u'Tom', self.reset, u'hates not Sarah but',
                       self.c2, u'Peter Parker', self.reset, u'.']))


class HumanValidationTests(ManagerTestCase):

    def setUp(self):
        patcher = mock.patch.object(TerminalInterviewer, 'get_human_answer')
        self.mock_get_answer = patcher.start()
        self.addCleanup(patcher.stop)
        patcher = mock.patch.object(TerminalInterviewer, 'explain')
        self.mock_explain = patcher.start()
        self.addCleanup(patcher.stop)

    #def create_question(self, e1, e2, text, confidence=0.5):
    #    """Simplistic question creator. It's going to create something that will match
    #    data types, and just that.
    #    Probably internal offsets will not be good, but will not cause exceptions.
    #    Text shall not contain the keys for e1 and e2 (meaning it's not checked), but
    #    shall have at least 4 tokens.
    #    """
    #    e1 = EntityFactory(key=e1)
    #    e2 = EntityFactory(key=e2)
    #    tokens = text.split()
    #    ev = EvidenceFactory(
    #        fact__e1=e1, fact__e2=e2,
    #        occurrences__data=[(e1, 0, 1), (e2, 1, 2)],
    #        segment__tokens=tokens)
    #    return ev, confidence

    def test_questions_are_consulted_in_given_order(self):
        q1 = EvidenceFactory(markup='{Tom|Person*} eats {Pizza|Food**} happily .')
        q2 = EvidenceFactory(markup='{Tom|Person*} eats {Cheese|Food**} happily .')
        self.term = TerminalInterviewer([q1, q2], mock.MagicMock())
        self.term()
        self.assertEqual(self.mock_get_answer.call_count, 2)
        self.assertEqual(
            self.mock_get_answer.call_args_list,
            [mock.call(q1), mock.call(q2)])

    def test_YES_NO_answers_are_passed_with_callback_and_proceeds(self):
        q1 = EvidenceFactory(markup='{Tom|Person*} eats {Pizza|Food**} happily .')
        q2 = EvidenceFactory(markup='{Tom|Person*} eats {Cheese|Food**} happily .')
        callback = mock.MagicMock()
        self.term = TerminalInterviewer([q1, q2], callback)
        self.mock_get_answer.side_effect = [self.term.YES, self.term.NO]
        result = self.term()
        self.assertIsNone(result)
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(
            callback.call_args_list,
            [mock.call(q1, True), mock.call(q2, False)])

    def test_user_can_say_he_is_tired_and_no_more_questions_are_shown(self):
        q1 = EvidenceFactory(markup='{Tom|Person*} eats {Pizza|Food**} happily .')
        q2 = EvidenceFactory(markup='{Tom|Person*} eats {Cheese|Food**} happily .')
        self.term = TerminalInterviewer([q1, q2], mock.MagicMock())
        self.mock_get_answer.side_effect = [self.term.RUN, self.term.YES]
        result = self.term()
        # after user says is tired, no more questions
        self.assertEqual(self.mock_get_answer.call_count, 1)
        self.assertIsNone(result)

    def test_user_is_confused_then_callback_is_not_invoken_but_next_question_goes(self):
        q1 = EvidenceFactory(markup='{Tom|Person*} {Cheese|Food**} happily eats.')
        q2 = EvidenceFactory(markup='{Tom|Person*} eats {Pizza|Food**} happily .')
        q3 = EvidenceFactory(markup='{Tom|Person*} eats {Cheese|Food**} happily .')
        callback = mock.MagicMock()
        self.term = TerminalInterviewer([q1, q2, q3], callback)
        self.mock_get_answer.side_effect = [self.term.DONT_KNOW, self.term.YES,
                                            self.term.YES]
        result = self.term()
        self.assertEqual(callback.call_count, 2)
        self.assertEqual(
            callback.call_args_list,
            [mock.call(q2, True), mock.call(q3, True)])
        self.assertEqual(self.mock_get_answer.call_count, 3)
        self.assertIsNone(result)

    def test_custom_options_stop_execution_and_are_returned(self):
        CUSTOM = u'custom'
        q1 = EvidenceFactory(markup='{Tom|Person*} eats {Pizza|Food**} happily .')
        q2 = EvidenceFactory(markup='{Tom|Person*} eats {Cheese|Food**} happily .')
        self.term = TerminalInterviewer(
            [q1, q2], mock.MagicMock(),
            extra_options=[(CUSTOM, u'some explanation')])
        self.mock_get_answer.side_effect = [CUSTOM, self.term.YES]
        result = self.term()
        # after user picks custom option, no more questions, and returned option
        self.assertEqual(self.mock_get_answer.call_count, 1)
        self.assertEqual(result, CUSTOM)
