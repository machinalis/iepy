try:
    from unittest import mock
except ImportError:
    import mock

from unittest import TestCase

from iepy.combined_ner import CombinedNERRunner
from iepy.models import PreProcessSteps


class TestCombinedNERRunner(TestCase):

    def setUp(self):
        self.runner1 = mock.MagicMock()
        self.runner2 = mock.MagicMock()
        self.doc = mock.MagicMock()
        self.doc.was_preprocess_done.side_effect = lambda x: False

    def test_runners_called_when_not_done_before(self):
        runner1, runner2, doc = self.runner1, self.runner2, self.doc

        runner = CombinedNERRunner(runner1, runner2)
        runner(doc)

        runner1.assert_called_once_with(doc)
        runner2.assert_called_once_with(doc)

    def test_runners_called_when_override(self):
        runner1, runner2, doc = self.runner1, self.runner2, self.doc
        doc.was_preprocess_done.side_effect = lambda x: True

        runner = CombinedNERRunner(runner1, runner2, override=True)
        runner(doc)

        runner1.assert_called_once_with(doc)
        runner2.assert_called_once_with(doc)

    def test_runners_not_called_when_done_before(self):
        runner1, runner2, doc = self.runner1, self.runner2, self.doc
        doc.was_preprocess_done.side_effect = lambda x: True

        runner = CombinedNERRunner(runner1, runner2)
        runner(doc)

        self.assertFalse(runner1.called)
        self.assertFalse(runner2.called)

    def test_no_entities_are_lost(self):
        runner1, runner2, doc = self.runner1, self.runner2, self.doc
        
        def set_result(doc, entities):
            doc.get_preprocess_result.side_effect = lambda x: entities
        
        e1 = mock.MagicMock()
        e1.offset = 1
        e2 = mock.MagicMock()
        e2.offset = 2
        runner1.side_effect = lambda doc: set_result(doc, [e1])
        runner2.side_effect = lambda doc: set_result(doc, [e2])
        
        runner = CombinedNERRunner(runner1, runner2)
        runner(doc)
        doc.set_preprocess_result.assert_called_once_with(PreProcessSteps.ner, [e1, e2])

