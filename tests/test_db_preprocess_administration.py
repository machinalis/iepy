from unittest import TestCase
import mock

from documentmanager_case import DocumentManagerTestCase
from iepy.models import PreProcessSteps, InvalidPreprocessSteps
from factories import IEDocFactory
from timelapse import timekeeper


class TestDocumentsPreprocessMetadata(TestCase):

    def test_preprocess_steps(self):
        self.assertEqual(
            [p.name for p in PreProcessSteps],
            ['tokenization', 'segmentation', 'tagging', 'nerc'])

    def test_just_created_document_has_no_preprocess_done(self):
        doc = IEDocFactory()
        for step in PreProcessSteps:
            self.assertFalse(doc.was_preprocess_done(step))

    def test_get_preprocess_result_when_not_done_gives_nothing(self):
        doc = IEDocFactory()
        for step in PreProcessSteps:
            self.assertIsNone(doc.get_preprocess_result(step))

    def test_setting_tokenization_result_can_be_later_retrieved(self):
        doc = IEDocFactory()
        simple_tokens = doc.text.split()
        step = PreProcessSteps.tokenization
        doc.set_preprocess_result(step, simple_tokens)
        self.assertTrue(doc.was_preprocess_done(step))
        self.assertEqual(doc.get_preprocess_result(step), simple_tokens)

    def test_cannot_set_segmentation_if_not_tokenization_stored(self):
        doc = IEDocFactory(text='Some sentence.')
        segments = [0]
        step = PreProcessSteps.segmentation
        self.assertRaises(ValueError, doc.set_preprocess_result, step, segments)
        self.assertFalse(doc.was_preprocess_done(step))

    def test_cannot_set_segmentation_larger_than_tokens(self):
        # segmentation numers must be valid indexes of tokens list
        doc = IEDocFactory(text='Some sentence.')
        doc.set_preprocess_result(PreProcessSteps.tokenization, doc.text.split())
        segments = [35]
        step = PreProcessSteps.segmentation
        self.assertRaises(ValueError, doc.set_preprocess_result, step, segments)
        self.assertFalse(doc.was_preprocess_done(step))

    def test_segmentation_result_must_be_order_list_of_numbers(self):
        doc = IEDocFactory(text='Some sentence . And some other . Indeed!')
        segments = [7, 3, 0]
        step = PreProcessSteps.segmentation
        self.assertRaises(ValueError, doc.set_preprocess_result, step, segments)
        # also must be strictly ascending
        segments = [0, 0, 3]
        self.assertRaises(ValueError, doc.set_preprocess_result, step, segments)
        self.assertFalse(doc.was_preprocess_done(step))

    def test_setting_segmentation_result_can_be_later_retrieved(self):
        doc = IEDocFactory(text='Some sentence . And some other . Indeed!')
        doc.set_preprocess_result(PreProcessSteps.tokenization, doc.text.split())
        simple_segments = [0, 3, 7]
        step = PreProcessSteps.segmentation
        doc.set_preprocess_result(step, simple_segments)
        self.assertTrue(doc.was_preprocess_done(step))
        self.assertEqual(doc.get_preprocess_result(step), simple_segments)

    def test_cannot_set_tagging_result_of_different_cardinality_than_tokens(self):
        doc = IEDocFactory(text='Some sentence')
        doc.set_preprocess_result(PreProcessSteps.tokenization, doc.text.split())
        step = PreProcessSteps.tagging
        for tags in [['NN'], ['NN', 'POS', 'VB']]:
            self.assertRaises(ValueError, doc.set_preprocess_result, step, tags)
            self.assertFalse(doc.was_preprocess_done(step))

    def test_setting_tagging_result_can_be_later_retrieved(self):
        doc = IEDocFactory(text='Some sentence. And some other. Indeed!')
        tokens = doc.text.split()
        doc.set_preprocess_result(PreProcessSteps.tokenization, tokens)
        simeple_tags = ['NN' for token in tokens]
        step = PreProcessSteps.tagging
        doc.set_preprocess_result(step, simeple_tags)
        self.assertTrue(doc.was_preprocess_done(step))
        self.assertEqual(doc.get_preprocess_result(step), simeple_tags)


class TestStorePreprocessOutputSideEffects(TestCase):
    # Just one step. We'll assume that for the others is the same
    step = PreProcessSteps.tokenization

    def test_if_step_is_not_preprocessstep_error_is_raised(self):
        doc1 = IEDocFactory(text='').save()
        self.assertRaises(InvalidPreprocessSteps,
                          doc1.set_preprocess_result, 'spell it', [])

    def test_doc_is_returned(self):
        doc1 = IEDocFactory(text='')
        r = doc1.set_preprocess_result(self.step, [])
        self.assertEqual(r, doc1)

    def test_save_is_not_called_inside_of_set_method(self):
        doc1 = IEDocFactory(text='')
        with mock.patch.object(doc1, 'save') as save:
            doc1.set_preprocess_result(self.step, [])
            self.assertFalse(save.called)

    def test_preprocess_metadata_is_created_after_call(self):
        doc1 = IEDocFactory(text='')
        self.assertNotIn(self.step.name, doc1.preprocess_metadata)
        doc1.set_preprocess_result(self.step, [])
        self.assertIn(self.step.name, doc1.preprocess_metadata)

    def test_preprocess_metadata_has_done_at(self):
        doc1 = IEDocFactory(text='')
        with timekeeper() as interval:
            doc1.set_preprocess_result(self.step, [])
        mdata = doc1.preprocess_metadata[self.step.name]
        interval.assertHasDate(mdata['done_at'])


class TestDocumentManagerFiltersForPreprocess(DocumentManagerTestCase):

    def test_raw_documents_are_filtered(self):
        doc1 = IEDocFactory(text='').save()
        doc2 = IEDocFactory(text='something').save()
        raws = self.manager.get_raw_documents()
        self.assertIn(doc1, raws)
        self.assertNotIn(doc2, raws)

    def test_untokenized_documents_are_filtered(self):
        doc1 = IEDocFactory(text='').save()
        doc2 = IEDocFactory(text='something').save()
        doc3 = IEDocFactory(text='something nice').save()
        doc4 = IEDocFactory(text='').save()
        step = PreProcessSteps.tokenization
        doc3.set_preprocess_result(step, doc3.text.split()).save()
        doc4.set_preprocess_result(step, []).save()
        untokeneds = self.manager.get_documents_lacking_preprocess(step)
        self.assertIn(doc1, untokeneds)
        self.assertIn(doc2, untokeneds)
        self.assertNotIn(doc3, untokeneds)
        self.assertNotIn(doc4, untokeneds)

    def test_unsegmented_documents_are_filtered(self):
        doc1 = IEDocFactory(text='something nice').save()
        doc2 = IEDocFactory(text='something nicer').save()
        doc3 = IEDocFactory(text='something event nicer').save()
        tkn = PreProcessSteps.tokenization
        doc2.set_preprocess_result(tkn, doc2.text.split()).save()
        doc3.set_preprocess_result(tkn, doc3.text.split()).save()
        step = PreProcessSteps.segmentation
        doc3.set_preprocess_result(step, [0]).save()
        unsegmented = self.manager.get_documents_lacking_preprocess(step)
        self.assertIn(doc1, unsegmented)
        self.assertIn(doc2, unsegmented)
        self.assertNotIn(doc3, unsegmented)

