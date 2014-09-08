import unittest

from iepy.data.models import TextSegment, EntityInSegment, EntityOccurrence

from .factories import IEDocFactory, EntityFactory, TextSegmentFactory
from .manager_case import ManagerTestCase


class TextSegmentTest(unittest.TestCase):

    def setUp(self):
        self.d = IEDocFactory()

    def test_empty(self):
        c = TextSegment.build(self.d, 0, 0)
        self.assertEqual(c.document, self.d)
        self.assertEqual(c.text, "")
        self.assertEqual(c.offset, 0)
        self.assertEqual(c.tokens, [])
        self.assertEqual(c.postags, [])
        self.assertEqual(c.entities, [])

    def test_data_copied(self):
        d = self.d
        d.offsets = range(7)
        d.tokens =  list("ABCDEFG")
        d.postags = list("NNVANVA")
        d.text = "ABCDEFG"
        c = TextSegment.build(d, 2, 5)
        self.assertEqual(c.offset, 2)
        self.assertEqual(c.tokens, ["C", "D", "E"])
        self.assertEqual(c.postags, ["V", "A", "N"])
        self.assertEqual(c.entities, [])
        self.assertEqual(c.text, "CDE")

    def test_entities_captured(self):
        e1 = EntityFactory()
        e2 = EntityFactory(kind='location')
        d = self.d
        d.offsets = range(7)
        d.tokens =  list("ABCDEFG")
        d.postags = list("NNVANVA")
        occ = [
            EntityOccurrence(entity=e1, offset=0, offset_end=1, alias="AB"),
            EntityOccurrence(entity=e2, offset=3, offset_end=4, alias="D"),
            EntityOccurrence(entity=e1, offset=4, offset_end=5, alias="E"),
            EntityOccurrence(entity=e1, offset=6, offset_end=7, alias="G"),
        ]
        d.entities = occ
        c = TextSegment.build(d, 2, 5)

        self.assertEqual(len(c.entities), 2)
        # Check first entity found
        e = c.entities[0]
        self.assertEqual(e.key, e2.key)
        self.assertEqual(e.canonical_form, e2.canonical_form)
        self.assertEqual(e.kind, e2.kind)
        self.assertEqual(e.offset, 3 - 2)
        self.assertEqual(e.alias, "D")
        # Check second and last one
        e = c.entities[1]
        self.assertEqual(e.key, e1.key)
        self.assertEqual(e.canonical_form, e1.canonical_form)
        self.assertEqual(e.kind, e1.kind)
        self.assertEqual(e.offset, 4 - 2)
        self.assertEqual(e.alias, "E")


    def test_entities_captured_large(self):
        # This is a largeish example, mostly to check that the bisection
        # algorithm in TextSegment.build works ok
        e1 = EntityFactory()
        d = self.d
        # Try several sizes+intervals
        for L, (s, e) in [(240, (51, 142)), (1024, (80, 333)), (1023, (80, 333))]:
            d.offsets = range(L)
            d.tokens =  ["X"]*L
            d.postags = ["N"]*L
            # Add entity occurrences at prime positions (primality isn't relevant
            # here, just a way to generate an irregular but predictable distribution)
            # entity length is 1 for indices < 6 and of the form 6*k-1
            # entity length is 2 for indices of the form 6*k+1
            occ = []
            for i in range(2, L):
                if all(i % k != 0 for k in range(2, int(i ** 0.5 + 1))):
                    if i < 6 or i % 6 == 5 or i + 1 == L:
                        end = i+1
                    else:
                        end = i+2
                    occ.append(
                        EntityOccurrence(entity=e1, offset=i, offset_end=end, alias="X"),
                    )
            d.entities = occ
            c = TextSegment.build(d, s, e)
            # Check that the right boundaries were found
            l = next(i for (i,e) in enumerate(d.entities) if e.offset==c.offset+c.entities[0].offset)
            r = next(i for (i,e) in enumerate(d.entities) if e.offset==c.offset+c.entities[-1].offset)
            self.assertTrue(d.entities[l-1].offset < s <= d.entities[l].offset)
            self.assertTrue(d.entities[r].offset < e <= d.entities[r+1].offset)

    def test_sentence_information(self):
        d = self.d
        L = 100
        d.offsets = range(L)
        d.tokens =  ["X"]*L
        d.postags = ["N"]*L
        d.sentences = [0, 5, 35, 36, 41, 90]
        c = TextSegment.build(d, 30, 60)
        self.assertEqual(c.sentences, [5, 6, 11])

    def test_sentence_information_start(self):
        d = self.d
        L = 100
        d.offsets = range(L)
        d.tokens =  ["X"]*L
        d.postags = ["N"]*L
        d.sentences = [0, 5, 35, 36, 41, 90]
        c = TextSegment.build(d, 0, 60)
        self.assertEqual(c.sentences, [0, 5, 35, 36, 41])

    def test_entity_occurrence_pairs(self):
        e1 = EntityFactory()
        e2 = EntityFactory()
        e3 = EntityFactory()
        s = TextSegmentFactory()
        o11 = EntityInSegment(key=e1.key, kind=e1.kind, offset=0, offset_end=1)
        o12 = EntityInSegment(key=e2.key, kind=e2.kind, offset=1, offset_end=2)
        o21 = EntityInSegment(key=e1.key, kind=e1.kind, offset=2, offset_end=3)
        o22 = EntityInSegment(key=e2.key, kind=e2.kind, offset=3, offset_end=4)
        o31 = EntityInSegment(key=e3.key, kind=e3.kind, offset=4, offset_end=5)
        s.entities = [o11, o12, o21, o22, o31]
        ps = s.entity_occurrence_pairs(e1, e2)
        self.assertEqual(ps, [(0, 1), (0,3), (2, 1), (2, 3)])

    def test_entity_occurrence_pairs_does_not_repeat(self):
        e1 = EntityFactory()
        s = TextSegmentFactory()
        o11 = EntityInSegment(key=e1.key, kind=e1.kind, offset=0, offset_end=1)
        o21 = EntityInSegment(key=e1.key, kind=e1.kind, offset=1, offset_end=2)
        s.entities = [o11, o21]
        ps = s.entity_occurrence_pairs(e1, e1)
        self.assertEqual(ps, [(0, 1), (1, 0)])

    def test_kind_occurrence_pairs(self):
        e1 = EntityFactory(kind='person')
        e2 = EntityFactory(kind='location')
        e3 = EntityFactory(kind='location')
        s = TextSegmentFactory()
        o11 = EntityInSegment(key=e1.key, kind=e1.kind, offset=0, offset_end=1)
        o12 = EntityInSegment(key=e2.key, kind=e2.kind, offset=1, offset_end=2)
        o21 = EntityInSegment(key=e1.key, kind=e1.kind, offset=2, offset_end=3)
        o13 = EntityInSegment(key=e3.key, kind=e3.kind, offset=3, offset_end=4)
        s.entities = [o11, o12, o21, o13]
        ps = s.kind_occurrence_pairs('person', 'location')
        self.assertEqual(ps, [(0, 1), (0,3), (2, 1), (2, 3)])


class TestDocumentSegmenter(ManagerTestCase):

    ManagerClass = TextSegment

    def set_doc_length(self, n):
        self.doc.tokens = ["x"] * n
        self.doc.offsets = range(n)
        self.doc.postags = ["tag"] * n

    def add_entities(self, positions):
        e1 = EntityFactory()
        for p in positions:
            if isinstance(p, tuple):
                start, length = p
            else:
                start, length = p, 1
            self.doc.entities.append(
                EntityOccurrence(entity=e1, offset=start, offset_end=start + length, alias="AB"),
            )

    def setUp(self):
        self.doc = IEDocFactory()
        self.doc.save()
        super(TestDocumentSegmenter, self).setUp()

    def test_no_entities(self):
        self.set_doc_length(100)
        self.doc.build_contextual_segments(3)
        self.assertEqual(len(TextSegment.objects), 0)

    def test_1_entity(self):
        self.set_doc_length(100)
        self.add_entities([50])
        self.doc.build_contextual_segments(3)
        self.assertEqual(len(TextSegment.objects), 0)

    def test_far_entities(self):
        self.set_doc_length(100)
        self.add_entities([50, 60])
        self.doc.build_contextual_segments(5)
        self.assertEqual(len(TextSegment.objects), 0)

    def test_close_entities(self):
        self.set_doc_length(100)
        self.add_entities([50, 60])
        self.doc.build_contextual_segments(10)
        self.assertEqual(len(TextSegment.objects), 1)
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 40)
        self.assertEqual(len(s.tokens), 31)
        self.assertEqual(len(s.entities), 2)

    def test_overlap_elimination(self):
        self.set_doc_length(100)
        self.add_entities([50, 55, 60])
        self.doc.build_contextual_segments(5)
        self.assertEqual(len(TextSegment.objects), 1)
        # Check that the segment captured is the big one
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 45)
        self.assertEqual(len(s.tokens), 21)
        self.assertEqual(len(s.entities), 3)

    def test_entity_not_splitted(self):
        self.set_doc_length(100)
        self.add_entities([(48, 5), 55, (57, 6)])
        self.doc.build_contextual_segments(5)
        self.assertEqual(len(TextSegment.objects), 1)
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 43)
        self.assertEqual(len(s.tokens), 25)
        self.assertEqual(len(s.entities), 3)

    def test_valid_overlap(self):
        self.set_doc_length(100)
        self.add_entities([45, 49, 55, 60])
        self.doc.build_contextual_segments(5)
        self.assertEqual(len(TextSegment.objects), 2)
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 40)
        self.assertEqual(len(s.tokens), 15)
        self.assertEqual(len(s.entities), 2)
        s = TextSegment.objects[1]
        self.assertEqual(s.offset, 50)
        self.assertEqual(len(s.tokens), 16)
        self.assertEqual(len(s.entities), 2)

    def test_segments_on_edges(self):
        self.set_doc_length(100)
        self.add_entities([1, 2, 97, 98])
        self.doc.build_contextual_segments(5)
        self.assertEqual(len(TextSegment.objects), 2)
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 0)
        self.assertEqual(len(s.tokens), 8)
        self.assertEqual(len(s.entities), 2)
        s = TextSegment.objects[1]
        self.assertEqual(s.offset, 92)
        self.assertEqual(len(s.tokens), 8)
        self.assertEqual(len(s.entities), 2)

    def test_sentence_segmenter_limits(self):
        self.set_doc_length(100)
        self.add_entities([1, 2, 22, 23, 61, 80])
        self.doc.sentences = [0, 20, 50]
        self.doc.build_syntactic_segments()
        self.assertEqual(len(TextSegment.objects), 3)
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 0)
        self.assertEqual(len(s.tokens), 20)
        self.assertEqual(len(s.entities), 2)
        s = TextSegment.objects[1]
        self.assertEqual(s.offset, 20)
        self.assertEqual(len(s.tokens), 30)
        self.assertEqual(len(s.entities), 2)
        s = TextSegment.objects[2]
        self.assertEqual(s.offset, 50)
        self.assertEqual(len(s.tokens), 50)
        self.assertEqual(len(s.entities), 2)

    def test_sentence_segmenter_requires_2_entities(self):
        self.set_doc_length(100)
        self.add_entities([1, 2, 22])
        self.doc.sentences = [0, 20, 50]
        self.doc.build_syntactic_segments()
        self.assertEqual(len(TextSegment.objects), 1)
        s = TextSegment.objects[0]
        self.assertEqual(s.offset, 0)
        self.assertEqual(len(s.tokens), 20)
        self.assertEqual(len(s.entities), 2)



