import unittest

from .factories import IEDocFactory, EntityFactory
from .manager_case import ManagerTestCase
from iepy.models import TextSegment, EntityOccurrence


class TextSegmentTest(unittest.TestCase):

    def setUp(self):
        self.d = IEDocFactory()

    def test_empty(self):
        c = TextSegment.build(self.d, 0, 0, "foo")
        self.assertEqual(c.document, self.d)
        self.assertEqual(c.text, "foo")
        self.assertEqual(c.offset, 0)
        self.assertEqual(c.tokens, [])
        self.assertEqual(c.postags, [])
        self.assertEqual(c.entities, [])

    def test_data_copied(self):
        d = self.d
        d.offsets = range(7)
        d.tokens =  list("ABCDEFG")
        d.postags = list("NNVANVA")
        c = TextSegment.build(d, 2, 5, "CDE")
        self.assertEqual(c.offset, 2)
        self.assertEqual(c.tokens, ["C", "D", "E"])
        self.assertEqual(c.postags, ["V", "A", "N"])
        self.assertEqual(c.entities, [])

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
        c = TextSegment.build(d, 2, 5, "CDE")

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
                EntityOccurrence(entity=e1, offset=start, offset_end=start+length, alias="AB"),
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
    
