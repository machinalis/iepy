from unittest import TestCase

from iepy.preprocess import PreProcessPipeline
from tests.factories import SentencedIEDocFactory
from iepy.models import PreProcessSteps, Entity, EntityOccurrence
from iepy.ner import NERRunner, StanfordNERRunner


class TestNERRunner(TestCase):

    def test_ner_runner_is_calling_ner(self):
        doc = SentencedIEDocFactory(text='Rami Eid is studying . At Stony Brook University in NY')
        
        def ner(sent):
            entities = []
            for t in sent:
                if t in ['Rami', 'Eid']:
                    e = 'PERSON'                
                elif t in ['Stony', 'Brook', 'University']:
                    e = 'ORGANIZATION'
                else:
                    e = 'O'
                entities.append(e)
            return zip(sent, entities)
        
        ner_runner = NERRunner(ner)
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

    def test_ner_runner_finds_consecutive_entities(self):
        doc = SentencedIEDocFactory(text='The student Rami Eid Stony Brook University in NY')
        
        def ner(sent):
            entities = []
            for t in sent:
                if t in ['Rami', 'Eid']:
                    e = 'PERSON'                
                elif t in ['Stony', 'Brook', 'University']:
                    e = 'ORGANIZATION'
                else:
                    e = 'O'
                entities.append(e)
            return zip(sent, entities)
        
        ner_runner = NERRunner(ner)
        ner_runner(doc)
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.nerc))
        entities = doc.get_preprocess_result(PreProcessSteps.nerc)
        self.assertEqual(len(entities), 2)
        self.assertEqual(entities[0].offset, 2)
        self.assertEqual(entities[0].offset_end, 4)
        self.assertEqual(entities[0].entity.kind, 'person')
        self.assertEqual(entities[1].offset, 4)
        self.assertEqual(entities[1].offset_end, 7)
        self.assertEqual(entities[1].entity.kind, 'organization')


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

