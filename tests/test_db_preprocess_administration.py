from unittest import TestCase
from unittest import mock

from iepy.data.db import DocumentManager
from iepy.data.models import IEDocument
from iepy.preprocess.pipeline import PreProcessSteps
from iepy.preprocess.ner.base import FoundEntity
from iepy.preprocess.segmenter import RawSegment

from .factories import IEDocFactory, SentencedIEDocFactory, naive_tkn
from .manager_case import ManagerTestCase


class TestDocumentCreationThruManager(ManagerTestCase):
    sample_id = 'sample-id'
    sample_text = 'this is a sample text'
    sample_metadata = {'iepy': 'rocks'}
    docmanager = DocumentManager()

    def test_create_basic(self):
        doc = self.docmanager.create_document(self.sample_id, self.sample_text,
                                              self.sample_metadata)
        self.assertEqual(doc.human_identifier, self.sample_id)
        self.assertEqual(doc.text, self.sample_text)
        self.assertEqual(doc.metadata, self.sample_metadata)
        self.assertEqual(IEDocument.objects.count(), 1)

    def test_create_existent_does_nothing(self):
        doc = self.docmanager.create_document(self.sample_id, self.sample_text,
                                              self.sample_metadata)
        doc2 = self.docmanager.create_document(self.sample_id, self.sample_text,
                                               self.sample_metadata)
        self.assertEqual(doc, doc2)
        self.assertEqual(IEDocument.objects.count(), 1)

    def test_doc_text_and_metadata_are_updated_if_enabled(self):
        new_text = self.sample_text + ' but longer'
        new_metadata = {'something': 'different'}
        self.docmanager.create_document(self.sample_id, self.sample_text,
                                        self.sample_metadata)
        doc = self.docmanager.create_document(self.sample_id, new_text,
                                              new_metadata)
        self.assertNotEqual(doc.text, new_text)
        self.assertEqual(doc.text, self.sample_text)
        self.assertNotEqual(doc.metadata, new_metadata)
        self.assertEqual(doc.metadata, self.sample_metadata)
        doc = self.docmanager.create_document(self.sample_id, new_text,
                                              new_metadata, update_mode=True)
        self.assertEqual(doc.text, new_text)
        self.assertEqual(doc.metadata, new_metadata)


class TestDocumentsPreprocessMetadata(ManagerTestCase):

    def test_preprocess_steps(self):
        self.assertEqual(
            [p.name for p in PreProcessSteps],
            ['tokenization', 'sentencer', 'tagging', 'ner', 'segmentation'])

    def test_just_created_document_has_no_preprocess_done(self):
        doc = IEDocFactory()
        for step in PreProcessSteps:
            self.assertFalse(doc.was_preprocess_step_done(step))

    def test_cannot_set_sentencer_if_not_tokenization_stored(self):
        doc = IEDocFactory(text='Some sentence.')
        sentences = [0, 3]
        self.assertRaises(ValueError, doc.set_sentencer_result, sentences)
        self.assertFalse(doc.was_preprocess_step_done(PreProcessSteps.sentencer))

    def test_cannot_set_sentences_larger_than_tokens(self):
        # sentencer numbers must be valid indexes of tokens list
        doc = IEDocFactory(text='Some sentence.')
        doc.set_tokenization_result(naive_tkn(doc.text))
        sentences = [35]
        self.assertRaises(ValueError, doc.set_sentencer_result, sentences)
        self.assertFalse(doc.was_preprocess_step_done(PreProcessSteps.sentencer))

    def test_sentencer_result_must_be_ordered_list_of_numbers(self):
        doc = IEDocFactory(text='Some sentence . And some other . Indeed !')
        sentences = [7, 3, 0]
        self.assertRaises(ValueError, doc.set_sentencer_result, sentences)
        # also must be strictly ascending
        sentences = [0, 0, 3]
        self.assertRaises(ValueError, doc.set_sentencer_result, sentences)
        self.assertFalse(doc.was_preprocess_step_done(PreProcessSteps.sentencer))

    def test_cannot_set_tagging_result_of_different_cardinality_than_tokens(self):
        doc = IEDocFactory(text='Some sentence')
        doc.set_tokenization_result(naive_tkn(doc.text))
        step = PreProcessSteps.tagging
        for tags in [['NN'], ['NN', 'POS', 'VB']]:
            self.assertRaises(ValueError, doc.set_tagging_result, tags)
            self.assertFalse(doc.was_preprocess_step_done(step))

    def test_setting_tagging_result_can_be_later_retrieved(self):
        doc = IEDocFactory(text='Some sentence. And some other. Indeed !')
        tokens = naive_tkn(doc.text)
        doc.set_tokenization_result(tokens)
        simple_tags = ['NN' for token in tokens]
        doc.set_tagging_result(simple_tags)
        self.assertTrue(doc.was_preprocess_step_done(PreProcessSteps.tagging))


class TestStorePreprocessOutputSideEffects(ManagerTestCase):

    def doc_ready_for(self, desired_step, save=True):
        # creates and returns a new document, with all prev steps than "desired_step"
        # already in place (and saved unless explicitely stated), together with a
        # valid result for the desired step
        text = 'Hello world.'
        doc = IEDocFactory(text=text)
        sample_values = [
            (PreProcessSteps.tokenization, [(0, 'Hello'), (6, 'world'), (11, '.')]),
            (PreProcessSteps.sentencer, [0, 3]),
            (PreProcessSteps.tagging, ['NN', 'NN', '.']),
            (PreProcessSteps.ner, [FoundEntity('world', 'LOCATION', 'world', 1, 2)]),
            (PreProcessSteps.segmentation, [RawSegment(0, 3, None)]),
        ]
        for step, value in sample_values:
            if step == desired_step:
                if save:
                    doc.save()
                return doc, value
            else:
                setter = getattr(doc, 'set_%s_result' % step.name)
                doc = setter(value)

    def setter_of(self, doc, step):
        return getattr(doc, 'set_%s_result' % step.name)

    def test_setter_methods_return_same_document_with_result_stored(self):
        for step in PreProcessSteps:
            doc, value = self.doc_ready_for(step)
            setter = self.setter_of(doc, step)
            self.assertEqual(doc, setter(value))
            self.assertTrue(doc.was_preprocess_step_done(step))

    def test_setter_do_not_save(self):
        for step in PreProcessSteps:
            doc, value = self.doc_ready_for(step)
            setter = self.setter_of(doc, step)
            with mock.patch.object(doc, 'save') as doc_save:
                setter(value)
                self.assertFalse(doc_save.called)
                from_db = IEDocument.objects.get(pk=doc.pk)
                self.assertFalse(from_db.was_preprocess_step_done(step))


class TestDocumentManagerFiltersForPreprocess(ManagerTestCase):

    ManagerClass = DocumentManager

    def test_manager_itself_iterates_over_all_documents(self):
        doc1 = IEDocFactory(text='')
        doc2 = IEDocFactory(text='something')
        doc3 = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        self.assertIn(doc1, self.manager)
        self.assertIn(doc2, self.manager)
        self.assertIn(doc3, self.manager)

    def test_raw_documents_are_filtered(self):
        doc1 = IEDocFactory(text='')
        doc2 = IEDocFactory(text='something')
        raws = self.manager.get_raw_documents()
        self.assertIn(doc1, raws)
        self.assertNotIn(doc2, raws)

    def test_untokenized_documents_are_filtered(self):
        doc1 = IEDocFactory(text='')
        doc2 = IEDocFactory(text='something')
        doc3 = IEDocFactory(text='something nice')
        doc4 = IEDocFactory(text='')
        step = PreProcessSteps.tokenization
        doc3.set_tokenization_result(naive_tkn(doc3.text)).save()
        doc4.set_tokenization_result([]).save()
        untokeneds = self.manager.get_documents_lacking_preprocess(step)
        self.assertIn(doc1, untokeneds)
        self.assertIn(doc2, untokeneds)
        self.assertNotIn(doc3, untokeneds)
        self.assertNotIn(doc4, untokeneds)

    def test_unsentenced_documents_are_filtered(self):
        doc1 = IEDocFactory(text='something nice')
        doc2 = IEDocFactory(text='something nicer')
        doc3 = IEDocFactory(text='something even nicer')
        doc2.set_tokenization_result(naive_tkn(doc2.text)).save()
        doc3.set_tokenization_result(naive_tkn(doc3.text)).save()
        doc3.set_sentencer_result([0, 3]).save()
        unsentenced = self.manager.get_documents_lacking_preprocess(
            PreProcessSteps.sentencer)
        self.assertIn(doc1, unsentenced)
        self.assertIn(doc2, unsentenced)
        self.assertNotIn(doc3, unsentenced)


class TestDocumentSentenceIterator(TestCase):

    def test_right_number_of_sentences_are_returned(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        sentencing = doc.sentences
        sentences = [s for s in doc.get_sentences()]
        self.assertEqual(len(sentencing) - 1, len(sentences))

    def test_tokens_are_preserved(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        sentences = [s for s in doc.get_sentences()]
        output_tokens = sum(sentences, [])
        self.assertEqual(doc.tokens, output_tokens)
