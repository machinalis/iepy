import unittest

from .factories import IEDocFactory, EntityFactory
from iepy.models import TextChunk, EntityOccurrence

class TextChunkTest(unittest.TestCase):

    def setUp(self):
        self.d = IEDocFactory()

    def test_empty(self):
        c = TextChunk.build(self.d, 0, 0, "foo")
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
        c = TextChunk.build(d, 2, 5, "CDE")
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
            EntityOccurrence(entity=e1, offset=0, alias="AB"),
            EntityOccurrence(entity=e2, offset=3, alias="D"),
            EntityOccurrence(entity=e1, offset=4, alias="E"),
            EntityOccurrence(entity=e1, offset=6, alias="G"),
        ]
        d.entities = occ
        c = TextChunk.build(d, 2, 5, "CDE")

        self.assertEqual(len(c.entities), 2)
        # Check first entity found
        e = c.entities[0]
        self.assertEqual(e.key, e2.key)
        self.assertEqual(e.canonical_form, e2.canonical_form)
        self.assertEqual(e.kind, e2.kind)
        self.assertEqual(e.offset, 3-2)
        self.assertEqual(e.alias, "D")
        # Check second and last one
        e = c.entities[1]
        self.assertEqual(e.key, e1.key)
        self.assertEqual(e.canonical_form, e1.canonical_form)
        self.assertEqual(e.kind, e1.kind)
        self.assertEqual(e.offset, 4-2)
        self.assertEqual(e.alias, "E")

