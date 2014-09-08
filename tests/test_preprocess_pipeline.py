try:
    from unittest import mock
except ImportError:
    import mock

from unittest import TestCase

from iepy.preprocess.pipeline import PreProcessPipeline


class TestPreProcessPipeline(TestCase):

    def test_walk_document_applies_all_step_runners_to_the_given_doc(self):
        step1_runner = mock.MagicMock()
        step1_runner.side_effect = lambda x: x.call_order.append(1)
        step2_runner = mock.MagicMock()
        step2_runner.side_effect = lambda x: x.call_order.append(2)
        doc = mock.MagicMock()
        doc.call_order = []
        p = PreProcessPipeline([step1_runner, step2_runner], [])
        p.walk_document(doc)
        step1_runner.assert_called_once_with(doc)
        step2_runner.assert_called_once_with(doc)
        self.assertEqual(doc.call_order, [1, 2])

    def test_walk_document_applies_all_step_runners_again_if_they_were_already_run(self):
        step_runner1 = mock.MagicMock()
        p = PreProcessPipeline([step_runner1], [])
        doc = object()
        p.walk_document(doc)
        p.walk_document(doc)
        self.assertEqual(step_runner1.call_count, 2)

    def test_walk_document_itself_does_not_save_the_document(self):
        step_runner1 = mock.MagicMock()
        p = PreProcessPipeline([step_runner1], [])
        doc = mock.MagicMock()
        p.walk_document(doc)
        self.assertEqual(doc.save.call_count, 0)

    def test_process_step_in_batch_applies_runner_to_all_documents(self):
        # We take care that doesn't have attr "step"
        _runner = lambda x: x
        runner = mock.Mock(wraps=_runner)
        docs = [object() for i in range(5)]
        p = PreProcessPipeline([runner], docs)
        p.process_step_in_batch(runner)
        self.assertEqual(runner.call_count, len(docs))
        self.assertEqual(runner.call_args_list, [mock.call(d) for d in docs])

    def test_process_step_in_batch_does_nothing_with_previous_steps_runner(self):
        runner1 = mock.Mock(wraps=lambda x: x)
        runner2 = mock.Mock(wraps=lambda x: x)
        docs = [object() for i in range(5)]
        p = PreProcessPipeline([runner1, runner2], docs)
        p.process_step_in_batch(runner2)
        self.assertFalse(runner1.called)

    def test_process_step_in_batch_filter_docs_to_apply_if_has_attr_step(self):
        step_runner = mock.MagicMock()
        step_runner.step = 'something'
        all_docs = [object() for i in range(5)]
        docs_manager = mock.MagicMock()
        docs_manager.__iter__.return_value = all_docs
        docs_manager.get_documents_lacking_preprocess.side_effect = lambda x: all_docs[:2]
        # Ok, docs manager has 5 docs, but get_documents_lacking_preprocess will return
        # only 2 of them
        p = PreProcessPipeline([step_runner], docs_manager)
        p.process_step_in_batch(step_runner)
        docs_filter = docs_manager.get_documents_lacking_preprocess
        docs_filter.assert_called_once_with(step_runner.step)
        self.assertNotEqual(step_runner.call_count, 5)
        self.assertEqual(step_runner.call_count, 2)
        self.assertEqual(step_runner.call_args_list, [mock.call(d) for d in all_docs[:2]])

    def test_process_step_in_batch_does_not_call_docs_save(self):
        runner = mock.Mock(wraps=lambda x: x)
        docs = [mock.Mock() for i in range(5)]
        p = PreProcessPipeline([runner], docs)
        p.process_step_in_batch(runner)
        for d in docs:
            self.assertFalse(d.save.called)

    def test_process_everythin_calls_successively_process_step_in_batch(self):
        runner1 = mock.Mock(wraps=lambda x: x)
        runner2 = mock.Mock(wraps=lambda x: x)
        docs = [object() for i in range(5)]
        p = PreProcessPipeline([runner1, runner2], docs)
        with mock.patch.object(p, 'process_step_in_batch') as mock_batch:
            p.call_order = []
            mock_batch.side_effect = lambda r: p.call_order.append(r)
            p.process_everything()
            self.assertEqual(mock_batch.call_count, 2)
            self.assertEqual(mock_batch.call_args_list,
                             [mock.call(runner1), mock.call(runner2)])
        self.assertEqual(p.call_order, [runner1, runner2])
