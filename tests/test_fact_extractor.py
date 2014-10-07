# -*- coding: utf-8 -*-
import mock
from unittest import TestCase, skip

from featureforge.validate import BaseFeatureFixture, EQ, RAISES
from featureforge.feature import make_feature
import numpy
from scipy.sparse import csr_matrix

from future.builtins import str

from .factories import EvidenceFactory
from iepy.extraction.fact_extractor import (FactExtractor,
                                 bag_of_words,
                                 bag_of_pos,
                                 bag_of_word_bigrams,
                                 bag_of_wordpos,
                                 bag_of_wordpos_bigrams,
                                 bag_of_words_in_between,
                                 bag_of_pos_in_between,
                                 bag_of_word_bigrams_in_between,
                                 bag_of_wordpos_in_between,
                                 bag_of_wordpos_bigrams_in_between,
                                 entity_order,
                                 entity_distance,
                                 other_entities_in_between,
                                 in_same_sentence,
                                 total_number_of_entities,
                                 verbs_count_in_between,
                                 verbs_count,
                                 symbols_in_between,
                                 BagOfVerbStems,
                                 BagOfVerbLemmas,
                                 LemmaBetween,
                                 MoreSamplesNeededException
                                 )
from iepy.extraction.fact_extractor import ColumnFilter
from iepy.utils import make_feature_list


def _e(markup, **kwargs):
    base_pos = kwargs.pop('base_pos', ["DT", u"JJ", u"NN"])
    evidence = EvidenceFactory(markup=markup, **kwargs)
    n = len(evidence.segment.tokens)
    pos = (base_pos * n)[:n]
    evidence.segment.postags = pos
    return evidence


class TestFactExtractor(TestCase):
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

    @mock.patch("iepy.fact_extractor.BagOfVerbStems", spec=True)
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


class TestBagOfWords(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_words)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set(u"drinking mate makes you go to the toilet".split())),
        test_eq2=(_e(u"Drinking"),
                  EQ, set(u"drinking".split())),
        test_eq3=(_e(u""),
                  EQ, set())
    )


class TestBagOfPos(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_pos)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set(u"DT JJ NN".split())),
        test_eq2=(_e(u"Drinking"),
                  EQ, set(u"DT".split())),
        test_eq3=(_e(u""),
                  EQ, set())
    )


class TestBagOfWordBigrams(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_word_bigrams)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {(u"drinking", u"mate"), (u"mate", u"makes"), (u"makes", u"you"),
                       (u"you", u"go"), (u"go", u"to"), (u"to", u"the"),
                       (u"the", u"toilet")}),
        test_eq2=(_e(u"Drinking mate"),
                  EQ, {(u"drinking", u"mate")}),
        test_eq3=(_e(u"Drinking"),
                  EQ, set()),
        test_eq4=(_e(u""),
                  EQ, set())
    )


class TestBagOfWordPos(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {(u"drinking", u"DT"), (u"mate", u"JJ"), (u"makes", u"NN"),
                       (u"you", u"DT"), (u"go", u"JJ"), (u"to", u"NN"), (u"the", u"DT"),
                       (u"toilet", u"JJ")}),
        test_eq2=(_e(u"Drinking"),
                  EQ, {(u"drinking", u"DT")}),
        test_eq3=(_e(u""),
                  EQ, set())
    )


class TestBagOfWordPosBigrams(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_bigrams)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {((u"drinking", u"DT"), (u"mate", u"JJ")),
                       ((u"mate", u"JJ"), (u"makes", u"NN")),
                       ((u"makes", u"NN"), (u"you", u"DT")),
                       ((u"you", u"DT"), (u"go", u"JJ")),
                       ((u"go", u"JJ"), (u"to", u"NN")),
                       ((u"to", u"NN"), (u"the", u"DT")),
                       ((u"the", u"DT"), (u"toilet", u"JJ")),
                       }),
        test_eq2=(_e(u"Drinking mate"),
                  EQ, {((u"drinking", u"DT"), (u"mate", u"JJ"))}),
        test_eq3=(_e(u"Drinking"),
                  EQ, set()),
        test_eq4=(_e(u""),
                  EQ, set())
    )


class TestBagOfWordsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_words_in_between)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set(u"makes you go to the".split())),
        test_eq2=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, set(u"makes you go to the".split())),
        test_eq3=(_e(u"Drinking {Mate|thing*} or {Tea|thing} makes you go to the {toilet|thing**}"),
                  EQ, set(u"or tea makes you go to the".split())),
        test_err=(_e(u"Drinking mate yeah"),
                  RAISES, ValueError),
        test_err2=(_e(u"Drinking {mate|thing*} yeah"),
                   RAISES, ValueError),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_eq5=(_e(u"{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfPosInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_pos_in_between)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set(u"DT JJ NN".split())),
        test_eq2=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, set(u"DT JJ NN".split())),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_eq5=(_e(u"{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfWordBigramsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_word_bigrams_in_between)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {(u"makes", u"you"), (u"you", u"go"), (u"go", u"to"), (u"to", u"the")}),
        test_eq2=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, {(u"makes", u"you"), (u"you", u"go"), (u"go", u"to"), (u"to", u"the")}),
        test_eq3=(_e(u"{Mate|thing*} makes you {toilet|thing**}"),
                  EQ, {(u"makes", u"you")}),
        test_eq4=(_e(u"{Mate|thing*} makes {toilet|thing**}"),
                  EQ, set()),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_eq6=(_e(u"{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfWordPosInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_in_between)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {(u"makes", u"NN"), (u"you", u"DT"), (u"go", u"JJ"), (u"to", u"NN"), (u"the", u"DT")}),
        test_eq2=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, {(u"makes", u"NN"), (u"you", u"DT"), (u"go", u"JJ"), (u"to", u"NN"), (u"the", u"DT")}),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
        test_eq6=(_e(u"{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfWordPosBigramsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_bigrams_in_between)
    fixtures = dict(
        test_eq1=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {((u"makes", u"NN"), (u"you", u"DT")),
                       ((u"you", u"DT"), (u"go", u"JJ")),
                       ((u"go", u"JJ"), (u"to", u"NN")),
                       ((u"to", u"NN"), (u"the", u"DT")),
                       }),
        test_eq2=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, {((u"makes", u"NN"), (u"you", u"DT")),
                       ((u"you", u"DT"), (u"go", u"JJ")),
                       ((u"go", u"JJ"), (u"to", u"NN")),
                       ((u"to", u"NN"), (u"the", u"DT")),
                       }),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
        test_eq6=(_e(u"{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestEntityOrder(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(entity_order)
    fixtures = dict(
        test_lr=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                 EQ, 1),
        test_rl=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                 EQ, 0),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestEntityDistance(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(entity_distance)
    fixtures = dict(
        test_lr=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                 EQ, 5),
        test_rl=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                 EQ, 5),
        test_multiword=(_e(u"Drinking {Argentinean Mate|thing*} the {toilet|thing**}"),
                        EQ, 1),
        test_zero=(_e(u"Drinking {Argentinean Mate|thing*} {toilet|thing**}"),
                   EQ, 0),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestOtherEntitiesInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(other_entities_in_between)
    fixtures = dict(
        test_lr=(_e(u"Drinking {Mate|thing*} makes {you|told} go to the {toilet|thing**}"),
                 EQ, 1),
        test_rl=(_e(u"Drinking {Mate|thing**} makes {you|told} go to the {toilet|thing*}"),
                 EQ, 1),
        test_many=(_e(u"Drinking {Mate|thing**} {makes|yeah} {you|told} {go|bad} {to|music} {the|aaa} {toilet|thing*}"),
                   EQ, 5),
        test_multiword=(_e(u"Drinking {Argentinean Mate|thing*} {the|told} {toilet|thing**}"),
                        EQ, 1),
        test_zero=(_e(u"Drinking {Argentinean Mate|thing*} {toilet|thing**}"),
                   EQ, 0),
        test_zero2=(_e(u"Drinking {Argentinean Mate|thing*} the {toilet|thing**}"),
                    EQ, 0),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestTotalEntitiesNumber(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(total_number_of_entities)
    fixtures = dict(
        test_lr=(_e(u"Drinking {Mate|thing*} makes {you|told} go to the {toilet|thing**}"),
                 EQ, 3),
        test_rl=(_e(u"Drinking {Mate|thing**} makes {you|told} go to the {toilet|thing*}"),
                 EQ, 3),
        test_many=(_e(u"Drinking {Mate|thing**} {makes|yeah} {you|told} {go|bad} {to|music} {the|aaa} {toilet|thing*}"),
                   EQ, 7),
        test_multiword=(_e(u"Drinking {Argentinean Mate|thing*} {the|told} {toilet|thing**}"),
                        EQ, 3),
        test_zero=(_e(u"Drinking {Argentinean Mate|thing*} {toilet|thing**}"),
                   EQ, 2),
        test_zero2=(_e(u"Drinking {Argentinean Mate|thing*} the {toilet|thing**}"),
                    EQ, 2),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestVerbsInBetweenEntitiesCount(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(verbs_count_in_between)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, 0),
        test_all=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", u"VBD"]),
                  EQ, 5),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestVerbsTotalCount(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(verbs_count)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, 0),
        test_all=(_e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", u"VBD"]),
                  EQ, 9),
        test_empty=(_e(u""),
                    EQ, 0),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        EQ, 0),
    )


class TestSymbolsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(symbols_in_between)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                   EQ, 0),
        test_one=(_e(u"Drinking {Mate|thing**}, makes you go to the {toilet|thing*}"),
                  EQ, 1),
        test_two=(_e(u"Drinking {Mate|thing**}, makes you go, to the {toilet|thing*}"),
                  EQ, 1),  # its only boolean
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestBagStemVerbInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbStems(in_between=True)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, set()),
        test_all=(_e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", u"VBD"]),
                  EQ, {u'mak', u'you', u'go', u'to', u'the'}),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestBagStemVerb(TestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbStems(in_between=False)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, set()),
        test_all=(_e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", u"VBD"]),
                  EQ, {u'drink', u'argentin', u'mat', u'mak', u'you',
                       u'go', u'to', u'the', u'toilet'}),
        test_empty=(_e(u""),
                    EQ, set()),
        test_no_entity=(_e(u"Drinking mate yeah", base_pos=["VB", u"VBD"]),
                        EQ, {u'drink', u'mat', u'yeah'}),
    )


class TestBagLemmaVerbInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbLemmas(in_between=True)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, set()),
        test_all=(_e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", u"VBD"]),
                  EQ, {u'make', u'you', u'go', u'to', u'the'}),
        test_empty=(_e(u""),
                    RAISES, ValueError),
        test_no_entity=(_e(u"Drinking mate yeah"),
                        RAISES, ValueError),
    )


class TestBagLemmaVerb(TestCase, FeatureEvidenceBaseCase):
    feature = BagOfVerbLemmas(in_between=False)
    fixtures = dict(
        test_none=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, set()),
        test_all=(_e(u"Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", u"VBD"]),
                  EQ, {u'drink', u'argentinean', u'mate', u'make', u'you',
                       u'go', u'to', u'the', u'toilet'}),
        test_empty=(_e(u""),
                    EQ, set()),
        test_no_entity=(_e(u"Drinking mate yeah", base_pos=["VB", u"VBD"]),
                        EQ, {u'drink', u'mate', u'yeah'}),
    )


class TestLemmaBetween(TestCase, FeatureEvidenceBaseCase):
    feature = LemmaBetween('makes')
    fixtures = dict(
        test_lr=(_e(u"Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                   EQ, 1),
        test_rl=(_e(u"Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, 1),
        test_no=(_e(u"Drinking {Mate|thing**} takes you to the {toilet|thing*}"),
                  EQ, 0),
        test_before=(_e(u"Drinking makes {Mate|thing**} go to the {toilet|thing*}"),
                  EQ, 0),
        test_after=(_e(u"Drinking {Mate|thing**} in the {toilet|thing*} makes fun"),
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
