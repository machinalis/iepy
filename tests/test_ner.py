from unittest import TestCase

from iepy.preprocess import PreProcessPipeline
from tests.factories import SentencedIEDocFactory
from iepy.models import PreProcessSteps, IEDocument, Entity, EntityOccurrence
from iepy.ner import NERRunner, StanfordNERRunner
from tests.manager_case import ManagerTestCase


class TestNERRunner(ManagerTestCase):
    
    ManagerClass = IEDocument

    entity_map = {
        'Rami': 'PERSON', 
        'Eid': 'PERSON', 
        'Stony': 'ORGANIZATION',
        'Brook': 'ORGANIZATION',
        'University': 'ORGANIZATION',
    }
    
    def check_ner(self, doc, entities_triples):
        def ner(sent):
            return [(t, self.entity_map.get(t, 'O')) for t in sent]
        ner_runner = NERRunner(ner)
        ner_runner(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.nerc))
        entities = doc.get_preprocess_result(PreProcessSteps.nerc)
        self.assertEqual(len(entities), len(entities_triples))
        for e, (offset, offset_end, kind) in zip(entities, entities_triples):
            self.assertEqual(e.offset, offset)
            self.assertEqual(e.offset_end, offset_end)
            self.assertEqual(e.entity.kind, kind)
    
    def test_ner_runner_is_calling_ner(self):
        doc = SentencedIEDocFactory(text='Rami Eid is studying . At Stony Brook University in NY')        
        self.check_ner(doc, [(0, 2, 'person'), (6, 9, 'organization')])

    def test_ner_runner_finds_consecutive_entities(self):
        doc = SentencedIEDocFactory(text='The student Rami Eid Stony Brook University in NY')
        self.check_ner(doc, [(2, 4, 'person'), (4, 7, 'organization')])


class TestStanfordNERRunner(TestCase):

    def test_stanford_ner_is_called_if_found(self):
        doc = SentencedIEDocFactory(text='Rami Eid is studying . At Stony Brook University in NY')        
        ner_runner = StanfordNERRunner()
        ner_runner(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.nerc))
        entities = doc.get_preprocess_result(PreProcessSteps.nerc)
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].offset, 0)
        self.assertEqual(entities[0].offset_end, 2)
        self.assertEqual(entities[0].entity.kind, 'person')
        self.assertEqual(entities[1].offset, 6)
        self.assertEqual(entities[1].offset_end, 9)
        self.assertEqual(entities[1].entity.kind, 'organization')

