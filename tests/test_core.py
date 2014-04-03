import unittest

from iepy.core import Fact, Evidence, certainty, Knowledge, BootstrappedIEPipeline

class TestCertainty(unittest.TestCase):

    def test_certainty_certain_no(self):
        self.assertEqual(certainty(0), 1)

    def test_certainty_certain_yes(self):
        self.assertEqual(certainty(1), 1)

    def test_certainty_uncertain(self):
        self.assertEqual(certainty(0.5), 0.5)

    def test_certainty_unknown(self):
        self.assertEqual(certainty(None), 0.5)


class TestKnowledge(unittest.TestCase):

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
    
