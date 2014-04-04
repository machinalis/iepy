try:
    from unittest import mock
except ImportError:
    import mock

from unittest import TestCase

from iepy.combined_ner import CombinedNERRunner


class TestCombinedNERRunner(TestCase):

    def setUp(self):
        self.runner1 = mock.MagicMock()
        self.runner2 = mock.MagicMock()
        self.doc = mock.MagicMock()
    
    def test_runners_called_when_not_done_before(self):
        runner1, runner2, doc = self.runner1, self.runner2, self.doc
        doc.was_preprocess_done.side_effect = lambda x: False
        
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

