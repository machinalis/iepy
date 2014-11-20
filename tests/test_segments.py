import unittest

from iepy.data.models import TextSegment, EntityOccurrence
from iepy.preprocess.segmenter import RawSegment, SyntacticSegmenterRunner

from .factories import IEDocFactory, EntityFactory, EntityOccurrenceFactory, TextSegmentFactory
from .manager_case import ManagerTestCase


def RSF(offset=0, offset_end=0, entity_occurrences=None):
    # hand made RawSegmentFactory
    return RawSegment(offset, offset_end, entity_occurrences)


class TextSegmentCreationTest(ManagerTestCase):

    def setUp(self):
        self.d = IEDocFactory()

    def build_and_get_segment_from_raw(self, raw):
        self.d.set_segmentation_result([raw], override=True)
        return list(self.d.get_text_segments())[0].hydrate()

    def test_empty(self):
        s = self.build_and_get_segment_from_raw(RSF(0, 0))
        self.assertEqual(s.document, self.d)
        self.assertEqual(s.text, "")
        self.assertEqual(s.offset, 0)
        self.assertEqual(s.tokens, [])
        self.assertEqual(s.postags, [])
        self.assertEqual(list(s.get_entity_occurrences()), [])

    def test_data_copied_simple(self):
        d = self.d
        d.offsets_to_text = list(range(7))
        d.tokens = list("ABCDEFG")
        d.postags = list("NNVANVA")
        d.text = "ABCDEFG"
        s = self.build_and_get_segment_from_raw(RSF(2, 5))
        self.assertEqual(s.offset, 2)
        self.assertEqual(s.tokens, ["C", "D", "E"])
        self.assertEqual(s.postags, ["V", "A", "N"])
        self.assertEqual(list(s.get_entity_occurrences()), [])
        self.assertEqual(s.text, "CDE")

    def hack_document(self, text):
        # monkey patch the iedocument with some valid attributes
        # if text has repeated tokens, we are dead.
        # veeery naive punctuation symbols handling: "," and "." only.
        self.d.text = text
        pre_tokens = text.split()
        # punctuation handling
        self.d.tokens = []
        for tk in pre_tokens:
            for symbol in [',', '.']:
                if tk.endswith(symbol):
                    self.d.tokens.append(tk.strip(symbol))
                    self.d.tokens.append(symbol)
                    break
            else:
                self.d.tokens.append(tk)
        assert len(set(self.d.tokens)) == len(self.d.tokens)  # repeated tks check
        self.d.offsets_to_text = [self.d.text.index(t) for t in self.d.tokens]
        self.d.postags = ["NN" for t in self.d.tokens]

    def test_data_copied_complex(self):
        self.hack_document("The people around the world is crazy.")
        s = self.build_and_get_segment_from_raw(RSF(2, 5))
        self.assertEqual(s.tokens, ["around", "the", "world"])
        self.assertEqual(s.text, "around the world")
        s = self.build_and_get_segment_from_raw(RSF(4, 8))
        self.assertEqual(s.tokens, ["world", "is", "crazy", "."])
        self.assertEqual(s.text, "world is crazy.")

    def test_entities_capture_simple(self):
        self.hack_document("The people around the world is crazy.")
        self.d.save()
        eo = EntityOccurrenceFactory(document=self.d, offset=4, offset_end=5)
        s = self.build_and_get_segment_from_raw(RSF(2, 6))
        self.assertEqual(list(s.get_entity_occurrences()), [eo])

    def test_hydrated_entity_occurrences_from_segment(self):
        # verify the segment offsets: ie, the goal is that obtaining tokens from
        # document or from segment shall be equivalent
        self.hack_document("The people around the world is crazy.")
        eo = EntityOccurrenceFactory(document=self.d, offset=3, offset_end=5)
        expected = ["the", "world"]
        assert self.d.tokens[eo.offset:eo.offset_end] == expected
        segm = self.build_and_get_segment_from_raw(RSF(2, 6))
        s_eo = list(segm.get_entity_occurrences())[0]
        self.assertEqual(
            segm.tokens[s_eo.segment_offset:s_eo.segment_offset_end],
            expected)

    def test_entities_capture_end_border(self):
        # check that occurrence ending on the last token is correcly captured
        self.hack_document("The people around the world is crazy.")
        eo = EntityOccurrenceFactory(document=self.d, offset=4, offset_end=5)
        s = self.build_and_get_segment_from_raw(RSF(2, 5))
        self.assertEqual(list(s.get_entity_occurrences()), [eo])

    def test_entities_capture_start_border(self):
        # check that occurrence starting on the first token is correcly captured
        self.hack_document("The people around the world is crazy.")
        eo = EntityOccurrenceFactory(document=self.d, offset=2, offset_end=3)
        s = self.build_and_get_segment_from_raw(RSF(2, 5))
        self.assertEqual(list(s.get_entity_occurrences()), [eo])

    def test_entities_capture_ending_outside_are_not_included(self):
        self.hack_document("The people around the world is crazy.")
        EntityOccurrenceFactory(document=self.d, offset=4, offset_end=6)
        s = self.build_and_get_segment_from_raw(RSF(2, 5))
        self.assertEqual(list(s.get_entity_occurrences()), [])

    def test_entities_capture_starting_before_are_not_included(self):
        self.hack_document("The people around the world is crazy.")
        EntityOccurrenceFactory(document=self.d, offset=1, offset_end=3)
        s = self.build_and_get_segment_from_raw(RSF(2, 5))
        self.assertEqual(list(s.get_entity_occurrences()), [])

    def test_sentence_information(self):
        d = self.d
        L = 100
        d.offsets = list(range(L))
        d.tokens = ["X"]*L
        d.postags = ["N"]*L
        d.sentences = [0, 5, 35, 36, 41, 90]
        d.syntactic_sentences = [""] * max(d.sentences)
        s = self.build_and_get_segment_from_raw(RSF(30, 60))
        self.assertEqual(s.sentences, [5, 6, 11])
        s = self.build_and_get_segment_from_raw(RSF(0, 60))
        self.assertEqual(s.sentences, [0, 5, 35, 36, 41])


class TestGetOccurrencesPairsFromSegment(ManagerTestCase):
    def setUp(self):
        self.s = TextSegmentFactory()
        self.d = self.s.document

    def create_occurrence(self, e, offset, end):
        return EntityOccurrenceFactory(document=self.d, entity=e,
                                       offset=offset, offset_end=end)

    def test_entity_occurrence_pairs(self):
        e1 = EntityFactory()
        e2 = EntityFactory()
        e3 = EntityFactory()
        # eo2_1 means: occurrence of entity "e2", first of them
        eo1_1 = self.create_occurrence(e1, 0, 1)
        eo2_1 = self.create_occurrence(e2, 1, 2)
        eo1_2 = self.create_occurrence(e1, 2, 3)
        eo2_2 = self.create_occurrence(e2, 3, 4)
        eo3_1 = self.create_occurrence(e3, 4, 5)
        self.s.entity_occurrences = [eo1_1, eo1_2, eo2_1, eo2_2, eo3_1]
        ps = self.s.entity_occurrence_pairs(e1, e2)
        self.assertEqual(ps, [(eo1_1, eo2_1), (eo1_1, eo2_2),
                              (eo1_2, eo2_1), (eo1_2, eo2_2)])

    def test_entity_occurrence_pairs_does_not_repeat(self):
        e1 = EntityFactory()
        o11 = self.create_occurrence(e1, 0, 1)
        o12 = self.create_occurrence(e1, 1, 2)
        self.s.entity_occurrences = [o11, o12]
        ps = self.s.entity_occurrence_pairs(e1, e1)
        self.assertEqual(ps, [(o11, o12), (o12, o11)])

    def test_kind_occurrence_pairs(self):
        e1 = EntityFactory(kind__name='person')
        e2 = EntityFactory(kind__name='location')
        e3 = EntityFactory(kind=e2.kind)
        eo1_1 = self.create_occurrence(e1, 0, 1)
        eo2_1 = self.create_occurrence(e2, 1, 2)
        eo1_2 = self.create_occurrence(e1, 2, 3)
        eo3_1 = self.create_occurrence(e3, 3, 4)
        self.s.entity_occurrences = [eo1_1, eo2_1, eo1_2, eo3_1]
        ps = self.s.kind_occurrence_pairs(e1.kind, e2.kind)
        self.assertEqual(ps, [(eo1_1, eo2_1), (eo1_1, eo3_1),
                              (eo1_2, eo2_1), (eo1_2, eo3_1)])


class TestDocumentSegmenter(ManagerTestCase):

    ManagerClass = TextSegment

    def setUp(self):
        self.doc = IEDocFactory()
        super(TestDocumentSegmenter, self).setUp()
        self.segmenter = SyntacticSegmenterRunner()

    def set_doc_length(self, n):
        self.doc.tokens = ["x"] * n
        self.doc.offsets = list(range(n))
        self.doc.postags = ["tag"] * n
        self.doc.sentences = [0]

    def add_entities(self, positions):
        e1 = EntityFactory()
        for p in positions:
            if isinstance(p, tuple):
                start, length = p
            else:
                start, length = p, 1
            EntityOccurrenceFactory(
                document=self.doc,
                entity=e1, offset=start,
                offset_end=start + length,
                alias="AB")

    def test_no_entities(self):
        self.set_doc_length(100)
        raws = self.segmenter.build_syntactic_segments(self.doc)
        self.assertEqual(raws, [])

    def test_sentence_segmenter_limits(self):
        self.set_doc_length(100)
        self.add_entities([1, 2, 22, 23, 35, 61, 80])
        self.doc.sentences = [0, 20, 50]
        raws = self.segmenter.build_syntactic_segments(self.doc)
        self.assertEqual(len(raws), 3)
        s = raws[0]
        self.assertEqual(s.offset, 0)
        self.assertEqual(s.offset_end, 20)
        self.assertEqual(len(s.entity_occurrences), 2)
        s = raws[1]
        self.assertEqual(s.offset, 20)
        self.assertEqual(s.offset_end, 50)
        self.assertEqual(len(s.entity_occurrences), 3)
        s = raws[2]
        self.assertEqual(s.offset, 50)
        self.assertEqual(s.offset_end, len(self.doc.tokens))
        self.assertEqual(len(s.entity_occurrences), 2)

    def test_sentence_segmenter_requires_2_entities(self):
        self.set_doc_length(100)
        self.add_entities([1, 2, 22])
        self.doc.sentences = [0, 20, 50]
        raws = self.segmenter.build_syntactic_segments(self.doc)
        self.assertEqual(len(raws), 1)
        s = raws[0]
        self.assertEqual(s.offset, 0)
        self.assertEqual(s.offset_end, 20)
        self.assertEqual(len(s.entity_occurrences), 2)
