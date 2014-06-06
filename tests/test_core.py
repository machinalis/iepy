try:
    from unittest import mock
except ImportError:
    import mock
import unittest

from sklearn.pipeline import Pipeline
from future.builtins import range

from iepy.core import BootstrappedIEPipeline
from iepy.knowledge import certainty, Knowledge
from .factories import EntityFactory, EvidenceFactory, FactFactory


class TestCertainty(unittest.TestCase):

    def test_certainty_certain_no(self):
        self.assertEqual(certainty(0), 1)

    def test_certainty_certain_yes(self):
        self.assertEqual(certainty(1), 1)

    def test_certainty_uncertain(self):
        self.assertEqual(certainty(0.5), 0.5)

    def test_certainty_unknown(self):
        self.assertEqual(certainty(None), 0.5)


class TestFactExtractionInterface(unittest.TestCase):

    def setUp(self):
        super(TestFactExtractionInterface, self).setUp()
        # given that we are not going to provide actual data, fitting will
        # fail. That's why its mocked here
        patcher = mock.patch.object(Pipeline, 'fit')
        self.mock_fit = patcher.start()
        self.addCleanup(patcher.stop)

    def get_evidence(self, relation):
        e1 = EntityFactory(key=u'Peter')
        e2 = EntityFactory(key=u'Sarah')
        tokens = [u'Peter', u'likes', u'Sarah', u'.']
        ev = EvidenceFactory(
            fact__e1=e1, fact__e2=e2, fact__relation=relation,
            occurrences__data=[(e1, 0, 1), (e2, 2, 3)],
            segment__tokens=tokens)
        return ev

    def build_training_knowledge(self, relations_dict):
        k = Knowledge()
        for relation_name, number in relations_dict.items():
            for i in range(number):
                ev = self.get_evidence(relation_name)
                k[ev] = (len(k) % 2 == 0)
        return k

    def test_one_fact_extractor_built_per_relation_in_available_data(self):
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_training_knowledge({'likes': 3, 'hates': 2})
        result = b.learn_fact_extractors(kn)
        self.assertEqual(len(result), 2)

    def test_no_fact_extractor_is_built_when_not_enough_data(self):
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_training_knowledge({'likes': 1, 'hates': 1, 'looks': 2})
        result = b.learn_fact_extractors(kn)
        self.assertEqual(len(result), 1)
        self.assertIn('looks', result)

    def test_fact_extractor_is_created_with_FactExtractorFactory(self):
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_training_knowledge({'likes': 3, 'hates': 2})
        with mock.patch('iepy.core.FactExtractorFactory') as m_FEF:
            b.learn_fact_extractors(kn)
        self.assertEqual(m_FEF.call_count, 2)

        actual_calls = [args for args, kwargs in m_FEF.call_args_list]
        expected_calls = [(b.extractor_config, k) for k in kn.per_relation().values()]
        self.assertEqual(len(actual_calls), len(expected_calls))
        for c in expected_calls:
            self.assertIn(c, actual_calls)

    def test_returned_fact_extractor_has_method_predict(self):
        # ie, can be used for scoring an evidence
        b = BootstrappedIEPipeline(mock.MagicMock(), [])
        kn = self.build_training_knowledge({'likes': 3})
        result = b.learn_fact_extractors(kn)
        predictor = list(result.values())[0]
        self.assertTrue(hasattr(predictor, 'predict'))
        self.assertTrue(callable(predictor.predict))
        self.assertTrue(hasattr(predictor, 'predict_proba'))
        self.assertTrue(callable(predictor.predict_proba))


class TestBootstrappedIEPipelineRelations(unittest.TestCase):

    def test_relations_are_infered_from_seeds(self):
        f1 = FactFactory(e1__kind=u'person', e2__kind=u'location',
                         relation=u'x')
        f2 = FactFactory(e1__kind=u'person', e2__kind=u'location',
                         relation=u'y')
        f3 = FactFactory(e1__kind=u'person', e2__kind=u'person',
                         relation=u'z')
        f4 = FactFactory(e1__kind=u'location', e2__kind=u'person',
                         relation=u'w')
        b = BootstrappedIEPipeline(mock.MagicMock(), [f1, f2, f3, f4])
        self.assertEqual(b.relations,
                         {u'x': (u'person', u'location'),
                          u'y': (u'person', u'location'),
                          u'z': (u'person', u'person'),
                          u'w': (u'location', u'person')}
                         )

    def test_conflictive_seeds_provoque_error(self):
        f1 = FactFactory(e1__kind=u'person', e2__kind=u'location',
                         relation=u'x')
        f2 = FactFactory(e1__kind=u'location', e2__kind=u'location',
                         relation=u'x')
        self.assertRaises(ValueError, BootstrappedIEPipeline,
                          mock.MagicMock(), [f1, f2])


class TestBootstrapAcceptingKnowledge(unittest.TestCase):
    """Step 6 of iepy takes the output of the classifier, and uses it for
    increasing the known things"""

    def setUp(self):
        self.threshold = 0.5
        self.b = BootstrappedIEPipeline(mock.MagicMock(), [],
                                        fact_threshold=self.threshold)
        assert len(self.b.knowledge) == 0

    def test_evidences_with_high_prediction_score_are_accepted(self):
        ev1 = EvidenceFactory()
        ev2 = EvidenceFactory()
        ev3 = EvidenceFactory()
        classifier_out = {ev1: 1, ev2: 0.5, ev3: 0.1}
        self.b.filter_facts(classifier_out)
        self.assertIn(ev1, self.b.knowledge)
        self.assertNotIn(ev2, self.b.knowledge)
        self.assertNotIn(ev3, self.b.knowledge)

    def test_no_accept_evidence_well_ranked_if_human_previously_rejected(self):
        ev1 = EvidenceFactory()
        classifier_out = {ev1: 1}
        self.b.answers[ev1] = 0
        self.b.filter_facts(classifier_out)
        self.assertNotIn(ev1, self.b.knowledge)

    def test_dropping_mode_discards_previous_not_human_knowledge(self):
        self.b.drop_guesses_each_round = True
        ev1 = EvidenceFactory()
        ev2 = EvidenceFactory()
        self.b.knowledge[ev1] = 1.0
        self.b.knowledge[ev2] = 1.0
        self.b.answers[ev1] = 1.0
        assert ev2 not in self.b.answers
        # Nothing new to add
        self.b.filter_facts({})
        # ev1 shall be preserved cause was human provided
        self.assertIn(ev1, self.b.knowledge)
        # ev2 not
        self.assertNotIn(ev2, self.b.knowledge)
