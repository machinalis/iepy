# -*- coding: utf-8 -*-
from unittest import TestCase, skip

from featureforge.validate import BaseFeatureFixture, EQ, RAISES
from featureforge.feature import make_feature

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
                                 verb_pos_count_in_between,
                                 verb_pos_count,
                                 symbols_in_between)


def _e(markup, **kwargs):
    base_pos = kwargs.pop('base_pos', ["DT", "JJ", "NN"])
    evidence = EvidenceFactory(markup=markup, **kwargs)
    n = len(evidence.segment.tokens)
    pos = (base_pos * n)[:n]
    evidence.segment.postags = pos
    return evidence


class FeatureEvidenceBaseCase(BaseFeatureFixture):

    @skip("skipped because there's no random generation of Evidences")
    def test_fuzz(self):
        pass


class TestBagOfWords(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_words)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("drinking mate makes you go to the toilet".split())),
        test_eq2=(_e("Drinking"),
                  EQ, set("drinking".split())),
        test_eq3=(_e(""),
                  EQ, set())
    )


class TestBagOfPos(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_pos)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("DT JJ NN".split())),
        test_eq2=(_e("Drinking"),
                  EQ, set("DT".split())),
        test_eq3=(_e(""),
                  EQ, set())
    )


class TestBagOfWordBigrams(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_word_bigrams)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {("drinking", "mate"), ("mate", "makes"), ("makes", "you"), ("you", "go"), ("go", "to"), ("to", "the"), ("the", "toilet")}),
        test_eq2=(_e("Drinking mate"),
                  EQ, {("drinking", "mate")}),
        test_eq3=(_e("Drinking"),
                  EQ, set()),
        test_eq4=(_e(""),
                  EQ, set())
    )


class TestBagOfWordPos(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {("drinking", "DT"), ("mate", "JJ"), ("makes", "NN"), ("you", "DT"), ("go", "JJ"), ("to", "NN"), ("the", "DT"), ("toilet", "JJ")}),
        test_eq2=(_e("Drinking"),
                  EQ, {("drinking", "DT")}),
        test_eq3=(_e(""),
                  EQ, set())
    )


class TestBagOfWordPosBigrams(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_bigrams)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {(("drinking", "DT"), ("mate", "JJ")),
                       (("mate", "JJ"), ("makes", "NN")),
                       (("makes", "NN"), ("you", "DT")),
                       (("you", "DT"), ("go", "JJ")),
                       (("go", "JJ"), ("to", "NN")),
                       (("to", "NN"), ("the", "DT")),
                       (("the", "DT"), ("toilet", "JJ")),
                       }),
        test_eq2=(_e("Drinking mate"),
                  EQ, {(("drinking", "DT"), ("mate", "JJ"))}),
        test_eq3=(_e("Drinking"),
                  EQ, set()),
        test_eq4=(_e(""),
                  EQ, set())
    )


class TestBagOfWordsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_words_in_between)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("makes you go to the".split())),
        test_eq2=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, set("makes you go to the".split())),
        test_eq3=(_e("Drinking {Mate|thing*} or {Tea|thing} makes you go to the {toilet|thing**}"),
                  EQ, set("or tea makes you go to the".split())),
        test_err=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
        test_err2=(_e("Drinking {mate|thing*} yeah"),
                  RAISES, ValueError),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_eq5=(_e("{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfPosInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_pos_in_between)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("DT JJ NN".split())),
        test_eq2=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, set("DT JJ NN".split())),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_eq5=(_e("{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfWordBigramsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_word_bigrams_in_between)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {("makes", "you"), ("you", "go"), ("go", "to"), ("to", "the")}),
        test_eq2=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, {("makes", "you"), ("you", "go"), ("go", "to"), ("to", "the")}),
        test_eq3=(_e("{Mate|thing*} makes you {toilet|thing**}"),
                  EQ, {("makes", "you")}),
        test_eq4=(_e("{Mate|thing*} makes {toilet|thing**}"),
                  EQ, set()),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_eq6=(_e("{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfWordPosInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_in_between)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {("makes", "NN"), ("you", "DT"), ("go", "JJ"), ("to", "NN"), ("the", "DT")}),
        test_eq2=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, {("makes", "NN"), ("you", "DT"), ("go", "JJ"), ("to", "NN"), ("the", "DT")}),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
        test_eq6=(_e("{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestBagOfWordPosBigramsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(bag_of_wordpos_bigrams_in_between)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {(("makes", "NN"), ("you", "DT")),
                       (("you", "DT"), ("go", "JJ")),
                       (("go", "JJ"), ("to", "NN")),
                       (("to", "NN"), ("the", "DT")),
                       }),
        test_eq2=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, {(("makes", "NN"), ("you", "DT")),
                       (("you", "DT"), ("go", "JJ")),
                       (("go", "JJ"), ("to", "NN")),
                       (("to", "NN"), ("the", "DT")),
                       }),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
        test_eq6=(_e("{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )


class TestEntityOrder(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(entity_order)
    fixtures = dict(
        test_lr=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, 1),
        test_rl=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, 0),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
    )


class TestEntityDistance(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(entity_distance)
    fixtures = dict(
        test_lr=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, 5),
        test_rl=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, 5),
        test_multiword=(_e("Drinking {Argentinean Mate|thing*} the {toilet|thing**}"),
                  EQ, 1),
        test_zero=(_e("Drinking {Argentinean Mate|thing*} {toilet|thing**}"),
                  EQ, 0),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
    )


class TestOtherEntitiesInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(other_entities_in_between)
    fixtures = dict(
        test_lr=(_e("Drinking {Mate|thing*} makes {you|told} go to the {toilet|thing**}"),
                  EQ, 1),
        test_rl=(_e("Drinking {Mate|thing**} makes {you|told} go to the {toilet|thing*}"),
                  EQ, 1),
        test_many=(_e("Drinking {Mate|thing**} {makes|yeah} {you|told} {go|bad} {to|music} {the|aaa} {toilet|thing*}"),
                  EQ, 5),
        test_multiword=(_e("Drinking {Argentinean Mate|thing*} {the|told} {toilet|thing**}"),
                  EQ, 1),
        test_zero=(_e("Drinking {Argentinean Mate|thing*} {toilet|thing**}"),
                  EQ, 0),
        test_zero2=(_e("Drinking {Argentinean Mate|thing*} the {toilet|thing**}"),
                  EQ, 0),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
    )


class TestTotalEntitiesNumber(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(total_number_of_entities)
    fixtures = dict(
        test_lr=(_e("Drinking {Mate|thing*} makes {you|told} go to the {toilet|thing**}"),
                  EQ, 3),
        test_rl=(_e("Drinking {Mate|thing**} makes {you|told} go to the {toilet|thing*}"),
                  EQ, 3),
        test_many=(_e("Drinking {Mate|thing**} {makes|yeah} {you|told} {go|bad} {to|music} {the|aaa} {toilet|thing*}"),
                  EQ, 7),
        test_multiword=(_e("Drinking {Argentinean Mate|thing*} {the|told} {toilet|thing**}"),
                  EQ, 3),
        test_zero=(_e("Drinking {Argentinean Mate|thing*} {toilet|thing**}"),
                  EQ, 2),
        test_zero2=(_e("Drinking {Argentinean Mate|thing*} the {toilet|thing**}"),
                  EQ, 2),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
    )


class TestVerbsInBetweenEntitiesCount(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(verb_pos_count_in_between)
    fixtures = dict(
        test_none=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, 0),
        test_all=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", "VBD"]),
                  EQ, 5),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
    )

class TestVerbsTotalCount(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(verb_pos_count)
    fixtures = dict(
        test_none=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}",
                      base_pos=["JJ"]),
                   EQ, 0),
        test_all=(_e("Drinking {Argentinean Mate|thing**} makes you go to the {toilet|thing*}",
                     base_pos=["VB", "VBD"]),
                  EQ, 9),
        test_empty=(_e(""),
                  EQ, 0),
        test_no_entity=(_e("Drinking mate yeah"),
                  EQ, 0),
    )


class TestSymbolsInBetween(TestCase, FeatureEvidenceBaseCase):
    feature = make_feature(symbols_in_between)
    fixtures = dict(
        test_none=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                   EQ, 0),
        test_one=(_e("Drinking {Mate|thing**}, makes you go to the {toilet|thing*}"),
                  EQ, 1),
        test_two=(_e("Drinking {Mate|thing**}, makes you go, to the {toilet|thing*}"),
                  EQ, 1),  # its only boolean
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_no_entity=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
    )
