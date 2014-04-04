from unittest import TestCase

from tests.factories import SentencedIEDocFactory, IEDocFactory
from iepy.models import PreProcessSteps, IEDocument
from iepy.ner import NERRunner, StanfordNERRunner
from tests.manager_case import ManagerTestCase


class NERTestMixin(object):

    entity_map = {
        'Rami': 'PERSON',
        'Eid': 'PERSON',
        'Stony': 'ORGANIZATION',
        'Brook': 'ORGANIZATION',
        'University': 'ORGANIZATION',
    }

    def check_ner(self, doc, entities_triples):
        def ner(sents):
            return [[(t, self.entity_map.get(t, 'O')) for t in sent] for sent in sents]
        ner_runner = NERRunner(ner)
        ner_runner(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.ner))
        entities = doc.get_preprocess_result(PreProcessSteps.ner)
        self.assertEqual(len(entities), len(entities_triples))
        for e, (offset, offset_end, kind) in zip(entities, entities_triples):
            self.assertEqual(e.offset, offset)
            self.assertEqual(e.offset_end, offset_end)
            self.assertEqual(e.entity.kind, kind)


class TestNERRunner(ManagerTestCase, NERTestMixin):

    ManagerClass = IEDocument

    def test_ner_runner_is_calling_ner(self):
        doc = SentencedIEDocFactory(
            text='Rami Eid is studying . At Stony Brook University in NY')
        self.check_ner(doc, [(0, 2, 'person'), (6, 9, 'organization')])

    def test_ner_runner_finds_consecutive_entities(self):
        doc = SentencedIEDocFactory(
            text='The student Rami Eid Stony Brook University in NY')
        self.check_ner(doc, [(2, 4, 'person'), (4, 7, 'organization')])


class TestStanfordNERRunner(ManagerTestCase, NERTestMixin):

    ManagerClass = IEDocument

    def test_stanford_ner_is_called_if_found(self):
        doc = SentencedIEDocFactory(
            text='Rami Eid is studying . At Stony Brook University in NY')
        ner_runner = StanfordNERRunner()
        ner_runner(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.ner))
        entities = doc.get_preprocess_result(PreProcessSteps.ner)
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].offset, 0)
        self.assertEqual(entities[0].offset_end, 2)
        self.assertEqual(entities[0].entity.kind, 'person')
        self.assertEqual(entities[1].offset, 6)
        self.assertEqual(entities[1].offset_end, 9)
        self.assertEqual(entities[1].entity.kind, 'organization')

    def test_runner_does_not_split_contractions(self):
        doc = IEDocFactory()
        tokens = list(enumerate(("I can't study with Rami Eid").split()))
        doc.set_preprocess_result(PreProcessSteps.tokenization, tokens)
        doc.set_preprocess_result(PreProcessSteps.sentencer, [0, len(tokens)])

        ner_runner = StanfordNERRunner()
        ner_runner(doc)
        result = doc.get_preprocess_result(PreProcessSteps.ner)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].offset, 4)
        self.assertEqual(result[0].offset_end, 6)
        self.assertEqual(result[0].alias, "Rami Eid")

    def test_if_runner_segments_can_still_keep_working(self):
        doc = IEDocFactory()
        tokens = list(enumerate(("This is a sentence . This is another with Rami Eid").split()))
        doc.set_preprocess_result(PreProcessSteps.tokenization, tokens)
        doc.set_preprocess_result(PreProcessSteps.sentencer, [0, len(tokens)])

        ner_runner = StanfordNERRunner()
        ner_runner(doc)
        result = doc.get_preprocess_result(PreProcessSteps.ner)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].offset, 9)
        self.assertEqual(result[0].offset_end, 11)
        self.assertEqual(result[0].alias, "Rami Eid")


