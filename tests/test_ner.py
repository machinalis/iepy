from iepy.data.models import IEDocument
from iepy.preprocess.ner.stanford import NERRunner, StanfordNERRunner
from iepy.preprocess.pipeline import PreProcessSteps
from .factories import SentencedIEDocFactory, IEDocFactory
from .manager_case import ManagerTestCase


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
        self.check_ner_result(doc, entities_triples)

    def check_ner_result(self, doc, entities_triples):
        self.assertTrue(doc.was_preprocess_step_done(PreProcessSteps.ner))
        entities = self.get_ner_result(doc)
        self.assertEqual(len(entities), len(entities_triples))
        for e, (offset, offset_end, kind) in zip(entities, entities_triples):
            self.assertEqual(e.offset, offset)
            self.assertEqual(e.offset_end, offset_end)
            self.assertEqual(e.entity.kind.name, kind)

    def get_ner_result(self, doc):
        # hacked ORM detail
        return list(doc.entity_occurrences.all())


class TestNERRunner(ManagerTestCase, NERTestMixin):

    ManagerClass = IEDocument

    def test_ner_runner_is_calling_ner(self):
        doc = SentencedIEDocFactory(
            text='Rami Eid is studying . At Stony Brook University in NY')
        self.check_ner(doc, [(0, 2, 'PERSON'), (6, 9, 'ORGANIZATION')])

    def test_ner_runner_finds_consecutive_entities(self):
        doc = SentencedIEDocFactory(
            text='The student Rami Eid Stony Brook University in NY')
        self.check_ner(doc, [(2, 4, 'PERSON'), (4, 7, 'ORGANIZATION')])

