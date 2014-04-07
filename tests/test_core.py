try:
    from unittest import mock
except ImportError:
    import mock
import unittest

from future.builtins import range

from iepy.core import Fact, Evidence, certainty, Knowledge, BootstrappedIEPipeline
from .factories import EntityFactory, EvidenceFactory


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


class TestFactExtractionInterface(unittest.TestCase):

    def get_evidence(self, relation):
        e1 = EntityFactory(key=u'Peter')
        e2 = EntityFactory(key=u'Sarah')
        tokens = [u'Peter', u'likes', u'Sarah', u'.']
        ev = EvidenceFactory(
            fact__e1=e1, fact__e2=e2, fact__relation=relation,
            occurrences__data=[(e1, 0, 1), (e2, 2, 3)],
            segment__tokens=tokens)
        return ev

    def build_knowledge(self, relations_dict):
        k = Knowledge()
        for relation_name, number in relations_dict.items():
            for i in range(number):
                ev = self.get_evidence(relation_name)
                k[ev] = 0.5
        return k

    def test_one_fact_extractor_built_per_relation_in_available_data(self):
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_knowledge({'likes': 3, 'hates': 2})
        result = b.learn_fact_extractors(kn)
        self.assertEqual(len(result), 2)

    def test_fact_extractor_is_created_with_FactExtractorFactory(self):
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_knowledge({'likes': 3, 'hates': 2})
        with mock.patch('iepy.core.FactExtractorFactory') as m_FEF:
            b.learn_fact_extractors(kn)
        self.assertEqual(m_FEF.call_count, 2)
        actual_calls = m_FEF.call_args_list
        expected_calls = [mock.call(b.extractor_config, k) for k in kn.per_relation().items()]
        self.assertEqual(actual_calls, expected_calls)

    def test_returned_fact_extractor_has_method_predict(self):
        # ie, can be used for scoring an evidence
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_knowledge({'likes': 3})
        result = b.learn_fact_extractors(kn)
        predictor = list(result.values())[0]
        self.assertTrue(hasattr(predictor, 'predict'))
        self.assertTrue(callable(predictor.predict))
