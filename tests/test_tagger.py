from unittest import TestCase

from iepy.preprocess import PreProcessPipeline
from tests.factories import SentencedIEDocFactory
from iepy.models import PreProcessSteps
from iepy.tagger import TaggerRunner, StanfordTaggerRunner


class TestTaggerRunner(TestCase):

    def test_tagger_runner_is_calling_postagger(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        expected_postags = [['DT', 'NN', '.'], ['CC', 'DT', 'JJ', '.'], ['RB', '.']]
        i = iter(expected_postags)
        def postagger(sent):
            return zip(sent, next(i))
        tag = TaggerRunner(postagger)
        tag(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.tagging))
        postags = doc.get_preprocess_result(PreProcessSteps.tagging)
        self.assertEqual(postags, sum(expected_postags, []))

    def test_tagger_runner_not_overriding_by_default(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        postagger1 = lambda sent: [(x, 'A') for x in sent]
        postagger2 = lambda sent: [(x, 'B') for x in sent]
        tag = TaggerRunner(postagger1)
        tag(doc)
        tag.postagger = postagger2 # XXX: accessing implementation
        tag(doc)
        postags = doc.get_preprocess_result(PreProcessSteps.tagging)
        self.assertTrue(all(x == 'A' for x in postags))
        
    def test_tagger_runner_overriding_when_selected(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        postagger1 = lambda sent: [(x, 'A') for x in sent]
        postagger2 = lambda sent: [(x, 'B') for x in sent]
        tag = TaggerRunner(postagger1, override=True)
        tag(doc)
        tag.postagger = postagger2 # XXX: accessing implementation
        tag(doc)
        postags = doc.get_preprocess_result(PreProcessSteps.tagging)
        self.assertTrue(all(x == 'B' for x in postags))


class TestStanfordTaggerRunner(TestCase):

    def test_stanford_tagger_is_called_if_found(self):
        doc = SentencedIEDocFactory(text='Some sentence. And some other. Indeed!')
        expected_postags = ['DT', 'NN', '.', 'CC', 'DT', 'JJ', '.', 'RB', '.']
        tag = StanfordTaggerRunner()
        tag(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.tagging))
        postags = doc.get_preprocess_result(PreProcessSteps.tagging)
        self.assertEqual(postags, expected_postags)

