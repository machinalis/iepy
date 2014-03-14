from unittest import TestCase

from iepy.preprocess import PreProcessPipeline
from tests.factories import SentencedIEDocFactory
from iepy.models import PreProcessSteps
from iepy.tagger import StanfordTaggerRunner


class TestStanfordTaggerRunner(TestCase):

    def test_tagger_is_loading_and_running(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        tag = StanfordTaggerRunner()
        tag(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.tagging))
        postags = doc.get_preprocess_result(PreProcessSteps.tagging)
        expected_postags = ['DT', 'NN', '.', 'CC', 'DT', 'JJ', '.', 'RB', '.']
        self.assertEqual(postags, expected_postags)
        
    def test_tagging_is_not_overriden(self):
        pass

    def test_tagging_is_overriden(self):
        #doc = SegmentedIEDocFactory(text='Some sentence. And some other. Indeed!')
        #tag = StanfordTaggerRunner(override=True)
        #tag(doc)
        pass

