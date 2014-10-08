# -*- coding: utf-8 -*-
import mock
from unittest import TestCase, skip

from featureforge.validate import BaseFeatureFixture, EQ, RAISES
from featureforge.feature import make_feature
import numpy
from scipy.sparse import csr_matrix

from iepy.data.db import CandidateEvidenceManager
from iepy.extraction.fact_extractor import (
    FactExtractor, bag_of_words, bag_of_pos, bag_of_word_bigrams, bag_of_wordpos,
    bag_of_wordpos_bigrams, bag_of_words_in_between, bag_of_pos_in_between,
    bag_of_word_bigrams_in_between, bag_of_wordpos_in_between,
    bag_of_wordpos_bigrams_in_between, entity_order, entity_distance,
    other_entities_in_between, in_same_sentence, total_number_of_entities,
    verbs_count_in_between, verbs_count, symbols_in_between, BagOfVerbStems,
    BagOfVerbLemmas, LemmaBetween, MoreSamplesNeededException)
from iepy.extraction.fact_extractor import ColumnFilter
from iepy.utils import make_feature_list

from .factories import EvidenceFactory
from .manager_case import ManagerTestCase


def _e(markup, **kwargs):
    base_pos = kwargs.pop('base_pos', ["DT", u"JJ", u"NN"])
    evidence = EvidenceFactory(markup=markup, **kwargs)
    evidence = CandidateEvidenceManager.hydrate(evidence)
    n = len(evidence.segment.tokens)
    pos = (base_pos * n)[:n]
    evidence.segment.postags = pos
    return evidence


class TestFactExtractor(ManagerTestCase):
    def setUp(self):
        self.config = {
            "classifier": "dtree",
            "classifier_args": dict(),
            "dimensionality_reduction": None,
            "dimensionality_reduction_dimension": None,
            "feature_selection": None,
            "feature_selection_dimension": None,
            "scaler": False,
            "sparse": True,
            "features": make_feature_list("""
                    bag_of_words
                    bag_of_pos
                    bag_of_word_bigrams
                    bag_of_wordpos
                    bag_of_wordpos_bigrams
                    bag_of_words_in_between
                    bag_of_pos_in_between
                    bag_of_word_bigrams_in_between
                    bag_of_wordpos_in_between
                    bag_of_wordpos_bigrams_in_between
                    entity_order
                    entity_distance
                    other_entities_in_between
                    in_same_sentence
                    verbs_count_in_between
                    verbs_count
                    total_number_of_entities
                    symbols_in_between
                    number_of_tokens
            """),
        }

    def test_simple_ok_configuration(self):
        FactExtractor(self.config)

    @mock.patch("iepy.extraction.fact_extractor.BagOfVerbStems", spec=True)
    def test_configuration_with_arguments(self, mocked_feature):
        patch = make_feature_list("""
            BagOfVerbStems True
            BagOfVerbLemmas True
            BagOfVerbLemmas False
        """)
        self.config["features"] = self.config["features"] + patch
        FactExtractor(self.config)
        self.assertEqual(mocked_feature.call_count, 1)
        self.assertEqual(mocked_feature.call_args, ((True, ), ))

    def test_error_missing_configuration(self):
        del self.config["dimensionality_reduction_dimension"]
        with self.assertRaises(ValueError):
            FactExtractor(self.config)

    def test_error_nonexistent_feature(self):
        self.config["features"].append("the_yeah_yeah_feature")
        with self.assertRaises(KeyError):
            FactExtractor(self.config)


class FeatureEvidenceBaseCase(BaseFeatureFixture):

    @skip(u"skipped because there's no random generation of Evidences")
    def test_fuzz(self):
        pass

    def test_fixtures(self):
        # here fixtures are database objects, so we are:
        #  - force to construct them on runtime, (ie, not when parsing tests classes)
        #  - better to construct them only once
        fixtures = {}
        for label, (markup, predicate, value) in self.fixtures.items():
            if callable(markup):
                datapoint = markup()
            else:
                datapoint = _e(markup)
            fixtures[label] = datapoint, predicate, value
        self.assert_feature_passes_fixture(self.feature, fixtures)


class TestBagOfWords(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_words)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, set(u"drinking mate makes you go to the toilet".split())),
        test_eq2=(u"Drinking",
                  EQ, set(u"drinking".split())),
        test_eq3=(u"",
                  EQ, set())
    )


class TestBagOfPos(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_pos)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, set(u"DT JJ NN".split())),
        test_eq2=(u"Drinking",
                  EQ, set(u"DT".split())),
        test_eq3=(u"",
                  EQ, set())
    )


class TestBagOfWordBigrams(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_word_bigrams)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, {(u"drinking", u"mate"), (u"mate", u"makes"), (u"makes", u"you"),
                       (u"you", u"go"), (u"go", u"to"), (u"to", u"the"),
                       (u"the", u"toilet")}),
        test_eq2=(u"Drinking mate",
                  EQ, {(u"drinking", u"mate")}),
        test_eq3=(u"Drinking",
                  EQ, set()),
        test_eq4=(u"",
                  EQ, set())
    )


class TestBagOfWordPos(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, {(u"drinking", u"DT"), (u"mate", u"JJ"), (u"makes", u"NN"),
                       (u"you", u"DT"), (u"go", u"JJ"), (u"to", u"NN"), (u"the", u"DT"),
                       (u"toilet", u"JJ")}),
        test_eq2=(u"Drinking",
                  EQ, {(u"drinking", u"DT")}),
        test_eq3=(u"",
                  EQ, set())
    )


class TestBagOfWordPosBigrams(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_bigrams)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, {((u"drinking", u"DT"), (u"mate", u"JJ")),
                       ((u"mate", u"JJ"), (u"makes", u"NN")),
                       ((u"makes", u"NN"), (u"you", u"DT")),
                       ((u"you", u"DT"), (u"go", u"JJ")),
                       ((u"go", u"JJ"), (u"to", u"NN")),
                       ((u"to", u"NN"), (u"the", u"DT")),
                       ((u"the", u"DT"), (u"toilet", u"JJ")),
                       }),
        test_eq2=(u"Drinking mate",
                  EQ, {((u"drinking", u"DT"), (u"mate", u"JJ"))}),
        test_eq3=(u"Drinking",
                  EQ, set()),
        test_eq4=(u"",
                  EQ, set())
    )


class TestBagOfWordsInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_words_in_between)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, set(u"makes you go to the".split())),
        test_eq2=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                  EQ, set(u"makes you go to the".split())),
        test_eq3=(u"Drinking {Mate|thing*} or {Tea|thing} makes you go to the {toilet|thing**}",
                  EQ, set(u"or tea makes you go to the".split())),
        test_eq5=(u"{Mate|thing**} {toilet|thing*}",
                  EQ, set()),
    )


class TestBagOfPosInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_pos_in_between)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, set(u"DT JJ NN".split())),
        test_eq2=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                  EQ, set(u"DT JJ NN".split())),
        test_eq3=(u"{Mate|thing**} {toilet|thing*}",
                  EQ, set()),
    )


class TestBagOfWordBigramsInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_word_bigrams_in_between)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, {(u"makes", u"you"), (u"you", u"go"), (u"go", u"to"), (u"to", u"the")}),
        test_eq2=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                  EQ, {(u"makes", u"you"), (u"you", u"go"), (u"go", u"to"), (u"to", u"the")}),
        test_eq3=(u"{Mate|thing*} makes you {toilet|thing**}",
                  EQ, {(u"makes", u"you")}),
        test_eq4=(u"{Mate|thing*} makes {toilet|thing**}",
                  EQ, set()),
        test_eq6=(u"{Mate|thing**} {toilet|thing*}",
                  EQ, set()),
    )


class TestBagOfWordPosInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_in_between)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, {(u"makes", u"NN"), (u"you", u"DT"), (u"go", u"JJ"), (u"to", u"NN"), (u"the", u"DT")}),
        test_eq2=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                  EQ, {(u"makes", u"NN"), (u"you", u"DT"), (u"go", u"JJ"), (u"to", u"NN"), (u"the", u"DT")}),
        test_eq6=(u"{Mate|thing**} {toilet|thing*}",
                  EQ, set()),
    )


class TestBagOfWordPosBigramsInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_bigrams_in_between)
    fixtures = dict(
        test_eq1=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                  EQ, {((u"makes", u"NN"), (u"you", u"DT")),
                       ((u"you", u"DT"), (u"go", u"JJ")),
                       ((u"go", u"JJ"), (u"to", u"NN")),
                       ((u"to", u"NN"), (u"the", u"DT")),
                       }),
        test_eq2=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                  EQ, {((u"makes", u"NN"), (u"you", u"DT")),
                       ((u"you", u"DT"), (u"go", u"JJ")),
                       ((u"go", u"JJ"), (u"to", u"NN")),
                       ((u"to", u"NN"), (u"the", u"DT")),
                       }),
        test_eq6=(u"{Mate|thing**} {toilet|thing*}",
                  EQ, set()),
    )


class TestEntityOrder(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(entity_order)
    fixtures = dict(
        test_lr=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                 EQ, 1),
        test_rl=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                 EQ, 0),
    )


class TestEntityDistance(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(entity_distance)
    fixtures = dict(
        test_lr=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                 EQ, 5),
        test_rl=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                 EQ, 5),
        test_multiword=(u"Drinking {Argentinean Mate|thing*} the {toilet|thing**}",
                        EQ, 1),
        test_zero=(u"Drinking {Argentinean Mate|thing*} {toilet|thing**}",
                   EQ, 0),
    )


class TestOtherEntitiesInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(other_entities_in_between)
    fixtures = dict(
        test_lr=(u"Drinking {Mate|thing*} makes {you|told} go to the {toilet|thing**}",
                 EQ, 1),
        test_rl=(u"Drinking {Mate|thing**} makes {you|told} go to the {toilet|thing*}",
                 EQ, 1),
        test_many=(u"Drinking {Mate|thing**} {makes|yeah} {you|told} {go|bad} {to|music} {the|aaa} {toilet|thing*}",
                   EQ, 5),
        test_multiword=(u"Drinking {Argentinean Mate|thing*} {the|told} {toilet|thing**}",
                        EQ, 1),
        test_zero=(u"Drinking {Argentinean Mate|thing*} {toilet|thing**}",
                   EQ, 0),
        test_zero2=(u"Drinking {Argentinean Mate|thing*} the {toilet|thing**}",
                    EQ, 0),
    )


class TestTotalEntitiesNumber(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(total_number_of_entities)
    fixtures = dict(
        test_lr=(u"Drinking {Mate|thing*} makes {you|told} go to the {toilet|thing**}",
                 EQ, 3),
        test_rl=(u"Drinking {Mate|thing**} makes {you|told} go to the {toilet|thing*}",
                 EQ, 3),
        test_many=(u"Drinking {Mate|thing**} {makes|yeah} {you|told} {go|bad} {to|music} {the|aaa} {toilet|thing*}",
                   EQ, 7),
        test_multiword=(u"Drinking {Argentinean Mate|thing*} {the|told} {toilet|thing**}",
                        EQ, 3),
        test_zero=(u"Drinking {Argentinean Mate|thing*} {toilet|thing**}",
                   EQ, 2),
        test_zero2=(u"Drinking {Argentinean Mate|thing*} the {toilet|thing**}",
                    EQ, 2),
    )


class TestVerbsInBetweenEntitiesCount(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(verbs_count_in_between)

    fixtures = dict(
        test_none=(
            lambda: _e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                       base_pos=["JJ"]),
            EQ, 0),
        test_all=(
            lambda: _e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                       base_pos=["VB", u"VBD"]),
            EQ, 5),
    )


class TestVerbsTotalCount(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(verbs_count)

    fixtures = dict(
        test_none=(
            lambda: _e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                       base_pos=["JJ"]),
            EQ, 0),
        test_all=(
            lambda: _e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                       base_pos=["VB", u"VBD"]),
            EQ, 9),
        test_empty=(u"",
                    EQ, 0),
        test_no_entity=(u"Drinking mate yeah",
                        EQ, 0),
    )


class TestSymbolsInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = make_feature(symbols_in_between)
    fixtures = dict(
        test_none=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                   EQ, 0),
        test_one=(u"Drinking {Mate|thing**}, makes you go to the {toilet|thing*}",
                  EQ, 1),
        test_two=(u"Drinking {Mate|thing**}, makes you go, to the {toilet|thing*}",
                  EQ, 1),  # its only boolean
    )


class TestBagStemVerbInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbStems(in_between=True)
    fixtures = dict(
        test_none=(
            lambda: _e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                       base_pos=["JJ"]),
            EQ, set()),
        test_all=(
            lambda: _e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                       base_pos=["VB", u"VBD"]),
            EQ, {u'mak', u'you', u'go', u'to', u'the'}),
    )


class TestBagStemVerb(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbStems(in_between=False)
    fixtures = dict(
        test_none=(
            lambda: _e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                       base_pos=["JJ"]),
            EQ, set()),
        test_all=(
            lambda: _e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                       base_pos=["VB", u"VBD"]),
            EQ, {u'drink', u'argentin', u'mat', u'mak', u'you',
                 u'go', u'to', u'the', u'toilet'}),
        test_empty=(u"", EQ, set()),
        test_no_entity=(lambda: _e(u"Drinking mate yeah", base_pos=["VB", u"VBD"]),
                        EQ, {u'drink', u'mat', u'yeah'}),
    )


class TestBagLemmaVerbInBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbLemmas(in_between=True)
    fixtures = dict(
        test_none=(
            lambda: _e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                       base_pos=["JJ"]),
            EQ, set()),
        test_all=(
            lambda: _e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                       base_pos=["VB", u"VBD"]),
            EQ, {u'make', u'you', u'go', u'to', u'the'}),
    )


class TestBagLemmaVerb(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbLemmas(in_between=False)
    fixtures = dict(
        test_none=(
            lambda: _e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                       base_pos=["JJ"]),
            EQ, set()),
        test_all=(
            lambda: _e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                       base_pos=["VB", u"VBD"]),
            EQ, {u'drink', u'argentinean', u'mate', u'make', u'you',
                 u'go', u'to', u'the', u'toilet'}),
        test_empty=(u"", EQ, set()),
        test_no_entity=(
            lambda: _e(u"Drinking mate yeah", base_pos=["VB", u"VBD"]),
            EQ, {u'drink', u'mate', u'yeah'}),
    )


class TestLemmaBetween(ManagerTestCase, FeatureEvidenceBaseCase):
    feature = LemmaBetween('makes')
    fixtures = dict(
        test_lr=(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                 EQ, 1),
        test_rl=(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                 EQ, 1),
        test_no=(u"Drinking {Mate|thing**} takes you to the {toilet|thing*}",
                 EQ, 0),
        test_before=(u"Drinking makes {Mate|thing**} go to the {toilet|thing*}",
                     EQ, 0),
        test_after=(u"Drinking {Mate|thing**} in the {toilet|thing*} makes fun",
                    EQ, 0),
    )


class TestDenseColumnFilter(TestCase):
    def setUp(self):
        self.X = numpy.array([
                [0, 1, 0, 0, 5],
                [0, 0, 0, 0, 0],
                [1, 0, 1, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0],
        ])
        self.N, self.M = self.X.shape

    def test_zero(self):
        cf = ColumnFilter(0)
        cf.fit(self.X)
        Y = cf.transform(self.X)
        self.assertTrue((self.X == Y).all())
        # the column mapping is the identity:
        mapping_ok = [cf.column_map(i) == i for i in range(Y.shape[1])]
        self.assertTrue(all(mapping_ok))

    def test_one(self):
        cf = ColumnFilter(1)
        cf.fit(self.X)
        Y = cf.transform(self.X)
        self.assertEqual(Y.shape, (self.N, self.M - 1))
        mask = numpy.array([True, True, True, False, True])
        self.assertTrue((Y == self.X[:, mask]).all())
        mapping = [cf.column_map(i) for i in range(Y.shape[1])]
        self.assertEqual(mapping, [i for i in range(self.M) if mask[i]])

    def test_all(self):
        cf = ColumnFilter(6)
        with self.assertRaises(MoreSamplesNeededException):
            cf.fit(self.X)


class TestSparseColumnFilter(TestCase):
    def setUp(self):
        self.X = csr_matrix([
                [0, 1, 0, 0, 5],
                [0, 0, 0, 0, 0],
                [1, 0, 1, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 1, 0, 0, 0],
                [0, 0, 0, 0, 0],
                [0, 0, 1, 0, 0],
                [0, 1, 0, 0, 0],
        ])
        self.N, self.M = self.X.shape

    def test_zero(self):
        cf = ColumnFilter(0)
        cf.fit(self.X)
        Y = cf.transform(self.X)
        # == is inefficient, use != and check number of nonzeros:
        self.assertTrue((self.X != Y).nnz == 0)
        # the column mapping is the identity:
        mapping_ok = [cf.column_map(i) == i for i in range(Y.shape[1])]
        self.assertTrue(all(mapping_ok))

    def test_one(self):
        cf = ColumnFilter(1)
        cf.fit(self.X)
        Y = cf.transform(self.X)
        self.assertEqual(Y.shape, (self.N, self.M - 1))
        mask = numpy.array([True, True, True, False, True])
        # == is inefficient, use != and check number of nonzeros:
        self.assertTrue((Y != self.X[:, mask]).nnz == 0)
        mapping = [cf.column_map(i) for i in range(Y.shape[1])]
        self.assertEqual(mapping, [i for i in range(self.M) if mask[i]])

    def test_all(self):
        cf = ColumnFilter(6)
        with self.assertRaises(MoreSamplesNeededException):
            cf.fit(self.X)
