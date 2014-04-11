# -*- coding: utf-8 -*-
from unittest import TestCase, skip

from featureforge.validate import BaseFeatureFixture, EQ, RAISES
from featureforge.feature import make_feature

from future.builtins import str

from .factories import EvidenceFactory
from iepy.fact_extractor import (bag_of_words,
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
                                 BagOfVerbLemmas
                                 )


def _e(markup, **kwargs):
    base_pos = kwargs.pop('base_pos', ["DT", u"JJ", u"NN"])
    evidence = EvidenceFactory(markup=markup, **kwargs)
    n = len(evidence.segment.tokens)
    pos = (base_pos * n)[:n]
    evidence.segment.postags = pos
    return evidence


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
