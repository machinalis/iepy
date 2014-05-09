import codecs
import csv
import tempfile
import unittest

from iepy.models import IEDocument
from iepy.knowledge import Evidence, Fact, Knowledge
from .factories import EvidenceFactory
from .manager_case import ManagerTestCase


class TestKnowledgeSimple(unittest.TestCase):

    def test_sorting(self):
        f = Fact(None, 'rel', None)
        e1 = Evidence(f, None, 0, 1)
        e2 = Evidence(f, None, 0, 2)
        e3 = Evidence(f, None, 0, 3)
        k = Knowledge()
        k[e1] = 1.0
        k[e2] = 0.5
        k[e3] = 0.1

        items = list(k.by_certainty())
        self.assertEqual(items, [(e1, 1.0), (e3, 0.1), (e2, 0.5)])

    def test_filtering(self):
        e1 = Evidence(Fact(None, 'rel', None), None, 0, 1)
        e2 = Evidence(Fact(None, 'other', None), None, 0, 1)
        e3 = Evidence(Fact(None, 'rel', None), None, 0, 2)
        k = Knowledge()
        k[e1] = 1.0
        k[e2] = 0.5
        k[e3] = 0.1

        items = k.per_relation()
        self.assertEqual(items, {
            'rel': Knowledge({e1: 1.0, e3: 0.1}),
            'other': Knowledge({e2: 0.5}),
        })


class TestKnowledgeCSV(ManagerTestCase):
    ManagerClass = IEDocument

    def setUp(self):
        self.ev = EvidenceFactory(
            markup="The physicist {Albert Einstein|person*} was born in "
            "{Germany|location} and died in the {United States|location**} .")

    def test_save_simple(self):
        k = Knowledge()
        score = 0.77
        k[self.ev] = score
        tmp = tempfile.NamedTemporaryFile()
        k.save_to_csv(tmp.name)
        with codecs.open(tmp.name, encoding='utf-8') as csvfile:
            csv_reader = csv.reader(csvfile)
            rows = list(csv_reader)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row[0], u'person')
        self.assertEqual(row[1], u'Albert Einstein')
        self.assertEqual(row[2], u'location')
        self.assertEqual(row[3], u'United States')
        self.assertEqual(row[4], self.ev.fact.relation)
        self.assertEqual(row[5], self.ev.segment.document.human_identifier)
        self.assertEqual(row[6], str(self.ev.segment.offset))
        self.assertEqual(row[7], '2')  # Number of tokens from segment of ent 1
        self.assertEqual(row[8], '12')  # Number of tokens from segment of ent 2
        self.assertEqual(row[9], str(score))

    def test_load_saved(self):
        self.ev.segment.document.save()
        self.ev.fact.e1.save()
        self.ev.fact.e2.save()
        self.ev.segment.save()
        k = Knowledge()
        score = 0.77
        k[self.ev] = score
        tmp = tempfile.NamedTemporaryFile()
        k.save_to_csv(tmp.name)
        k2 = Knowledge.load_from_csv(tmp.name)
        self.assertEqual(k, k2)
