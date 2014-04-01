import unittest

from iepy.core import Fact, Evidence, certainty, Knowledge, BootstrappedIEPipeline

class TestCertainty(unittest.TestCase):

    def test_certainty_certain_no(self):
        self.assertEqual(certainty(0), 1)

    def test_certainty_certain_yes(self):
        self.assertEqual(certainty(1), 1)

    def test_certainty_uncertain(self):
        self.assertEqual(certainty(0.5), 0.5)
    
