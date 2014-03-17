from unittest import TestCase
import mock

from manager_case import ManagerTestCase
from iepy.db import DocumentManager, TextSegmentManager
from iepy.models import (PreProcessSteps, InvalidPreprocessSteps,
                         EntityInSegment, Entity)
from factories import IEDocFactory, SentencedIEDocFactory, TextSegmentFactory, naive_tkn
from timelapse import timekeeper


class TestDocumentsPreprocessMetadata(TestCase):

    def test_preprocess_steps(self):
        self.assertEqual(
            [p.name for p in PreProcessSteps],
            ['tokenization', 'sentencer', 'tagging', 'nerc', 'segmentation'])

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
        simple_tokens = naive_tkn(doc.text)
        step = PreProcessSteps.tokenization
        doc.set_preprocess_result(step, simple_tokens)
        self.assertTrue(doc.was_preprocess_done(step))
        self.assertEqual(doc.get_preprocess_result(step), simple_tokens)

    def test_cannot_set_sentencer_if_not_tokenization_stored(self):
        doc = IEDocFactory(text='Some sentence.')
        sentences = [0, 3]
        step = PreProcessSteps.sentencer
        self.assertRaises(ValueError, doc.set_preprocess_result, step, sentences)
        self.assertFalse(doc.was_preprocess_done(step))

    def test_cannot_set_sentences_larger_than_tokens(self):
        # sentencer numbers must be valid indexes of tokens list
        doc = IEDocFactory(text='Some sentence.')
        doc.set_preprocess_result(PreProcessSteps.tokenization, naive_tkn(doc.text))
        sentences = [35]
        step = PreProcessSteps.sentencer
        self.assertRaises(ValueError, doc.set_preprocess_result, step, sentences)
        self.assertFalse(doc.was_preprocess_done(step))

    def test_sentencer_result_must_be_ordered_list_of_numbers(self):
        doc = IEDocFactory(text='Some sentence . And some other . Indeed !')
        sentences = [7, 3, 0]
        step = PreProcessSteps.sentencer
        self.assertRaises(ValueError, doc.set_preprocess_result, step, sentences)
        # also must be strictly ascending
        sentences = [0, 0, 3]
        self.assertRaises(ValueError, doc.set_preprocess_result, step, sentences)
        self.assertFalse(doc.was_preprocess_done(step))

    def test_setting_sentencer_result_can_be_later_retrieved(self):
        doc = IEDocFactory(text='Some sentence . And some other . Indeed !')
        doc.set_preprocess_result(PreProcessSteps.tokenization, naive_tkn(doc.text))
        simple_sentences = [0, 3, 7, 9]
        step = PreProcessSteps.sentencer
        doc.set_preprocess_result(step, simple_sentences)
        self.assertTrue(doc.was_preprocess_done(step))
        self.assertEqual(doc.get_preprocess_result(step), simple_sentences)

    def test_cannot_set_tagging_result_of_different_cardinality_than_tokens(self):
        doc = IEDocFactory(text='Some sentence')
        doc.set_preprocess_result(PreProcessSteps.tokenization, naive_tkn(doc.text))
        step = PreProcessSteps.tagging
        for tags in [['NN'], ['NN', 'POS', 'VB']]:
            self.assertRaises(ValueError, doc.set_preprocess_result, step, tags)
            self.assertFalse(doc.was_preprocess_done(step))

    def test_setting_tagging_result_can_be_later_retrieved(self):
        doc = IEDocFactory(text='Some sentence. And some other. Indeed !')
        tokens = naive_tkn(doc.text)
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


class TestDocumentManagerFiltersForPreprocess(ManagerTestCase):

    ManagerClass = DocumentManager

    def test_manager_itself_iterates_over_all_documents(self):
        doc1 = IEDocFactory(text='').save()
        doc2 = IEDocFactory(text='something').save()
        doc3 = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!').save()
        self.assertIn(doc1, self.manager)
        self.assertIn(doc2, self.manager)
        self.assertIn(doc3, self.manager)

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
        doc3.set_preprocess_result(step, naive_tkn(doc3.text)).save()
        doc4.set_preprocess_result(step, []).save()
        untokeneds = self.manager.get_documents_lacking_preprocess(step)
        self.assertIn(doc1, untokeneds)
        self.assertIn(doc2, untokeneds)
        self.assertNotIn(doc3, untokeneds)
        self.assertNotIn(doc4, untokeneds)

    def test_unsentenced_documents_are_filtered(self):
        doc1 = IEDocFactory(text='something nice').save()
        doc2 = IEDocFactory(text='something nicer').save()
        doc3 = IEDocFactory(text='something even nicer').save()
        tkn = PreProcessSteps.tokenization
        doc2.set_preprocess_result(tkn, naive_tkn(doc2.text)).save()
        doc3.set_preprocess_result(tkn, naive_tkn(doc3.text)).save()
        step = PreProcessSteps.sentencer
        doc3.set_preprocess_result(step, [0, 3]).save()
        unsentenced = self.manager.get_documents_lacking_preprocess(step)
        self.assertIn(doc1, unsentenced)
        self.assertIn(doc2, unsentenced)
        self.assertNotIn(doc3, unsentenced)


class TestDocumentSentenceIterator(TestCase):

    def test_right_number_of_sentences_are_returned(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        sentencing = doc.get_preprocess_result(PreProcessSteps.sentencer)
        sentences = [s for s in doc.get_sentences()]
        self.assertEqual(len(sentencing) - 1, len(sentences))

    def test_tokens_are_preserved(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        offset_tokens = doc.get_preprocess_result(PreProcessSteps.tokenization)
        sentences = [s for s in doc.get_sentences()]
        output_tokens = sum(sentences, [])
        self.assertEqual([t for o, t in offset_tokens], output_tokens)


class TestSegmentFilters(ManagerTestCase):

    ManagerClass = TextSegmentManager

    def setUp(self):
        super(TestSegmentFilters, self).setUp()
        d = IEDocFactory()
        d.save()
        # Build 3 Segments, referring to 2 entities:
        #  * Segment 1 refers to A
        #  * Segment 2 refers to A+B
        #  * Segment 3 refers to B, twice

        s1 = TextSegmentFactory(document=d)
        s1.entities.append(EntityInSegment(
            key="A", canonical_form="Entity1", kind="person", offset=1, offset_end=2
        ))
        s1.save()
        s2 = TextSegmentFactory(document=d)
        s2.entities.append(EntityInSegment(
            key="A", canonical_form="Entity1", kind="person", offset=1, offset_end=2
        ))
        s2.entities.append(EntityInSegment(
            key="B", canonical_form="Entity2", kind="location", offset=1, offset_end=2
        ))
        s2.save()
        s3 = TextSegmentFactory(document=d)
        s3.entities.append(EntityInSegment(
            key="B", canonical_form="Entity2", kind="location", offset=1, offset_end=2
        ))
        s3.entities.append(EntityInSegment(
            key="B", canonical_form="Entity2", kind="location", offset=2, offset_end=3
        ))
        s3.save()
        self.s1, self.s2, self.s3 = s1, s2, s3

    def test_both_entities(self):
        # Request for entities A and B, only Segment 2 should be returned
        ea = Entity(key="A")
        eb = Entity(key="B")
        segments = self.manager.segments_with_both_entities(ea, eb)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], self.s2)

    def test_both_kinds(self):
        # Request for kinds person+location, only Segment 2 should be returned
        segments = self.manager.segments_with_both_kinds("person", "location")
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], self.s2)

    def test_both_kinds_duplicate(self):
        # Request for kinds location+location. Only Segment 3 should be returned
        # because it has 2 locations. Segment 2 has a single location, so it is
        # not valid
        segments = self.manager.segments_with_both_kinds("location", "location")
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0], self.s3)
