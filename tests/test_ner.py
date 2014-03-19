from unittest import TestCase

from iepy.preprocess import PreProcessPipeline
from tests.factories import SentencedIEDocFactory
from iepy.models import PreProcessSteps, Entity, EntityOccurrence
from iepy.ner import NERRunner


class TestNERRunner(TestCase):

    def test_ner_runner_is_calling_ner(self):
        doc = SentencedIEDocFactory(text='Rami Eid is studying . At Stony Brook University in NY')
        #e1 = Entity(key='Rami Eid', canonical_form='Rami Eid', kind='person')
        #e2 = Entity(key='Stony Brook University', canonical_form='Stony Brook University', kind='person')
        #eo1 = EntityOccurrence(entity=e1, offset=0, offset_end=2)
        #eo2 = EntityOccurrence(entity=e2, offset=6, offset_end=9)
        #expected_entities = [eo1, eo2]
        
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
        self.assertEqual(entities[1].offset, 6)
        self.assertEqual(entities[1].offset_end, 9)

