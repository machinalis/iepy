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
                                 in_same_sentence)


def _e(markup):
    evidence = EvidenceFactory(markup=markup)
    n = len(evidence.segment.tokens)
    pos = (["DT", "JJ", "NN"] * n)[:n]
    evidence.segment.postags = pos
    return evidence


class TestBagOfWords(TestCase, BaseFeatureFixture):
    feature = make_feature(bag_of_words)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("drinking mate makes you go to the toilet".split())),
        test_eq2=(_e("Drinking"),
                  EQ, set("drinking".split())),
        test_eq3=(_e(""),
                  EQ, set())
    )

    @skip
    def test_fuzz(self):
        pass


class TestBagOfPos(TestCase, BaseFeatureFixture):
    feature = make_feature(bag_of_pos)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("DT JJ NN".split())),
        test_eq2=(_e("Drinking"),
                  EQ, set("DT".split())),
        test_eq3=(_e(""),
                  EQ, set())
    )

    @skip
    def test_fuzz(self):
        pass


class TestBagOfWordBigrams(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestBagOfWordPos(TestCase, BaseFeatureFixture):
    feature = make_feature(bag_of_wordpos)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, {("drinking", "DT"), ("mate", "JJ"), ("makes", "NN"), ("you", "DT"), ("go", "JJ"), ("to", "NN"), ("the", "DT"), ("toilet", "JJ")}),
        test_eq2=(_e("Drinking"),
                  EQ, {("drinking", "DT")}),
        test_eq3=(_e(""),
                  EQ, set())
    )

    @skip
    def test_fuzz(self):
        pass


class TestBagOfWordPosBigrams(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestBagOfWordsInBetween(TestCase, BaseFeatureFixture):
    feature = make_feature(bag_of_words_in_between)
    fixtures = dict(
        test_eq1=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                  EQ, set("makes you go to the".split())),
        test_eq2=(_e("Drinking {Mate|thing**} makes you go to the {toilet|thing*}"),
                  EQ, set("makes you go to the".split())),
        test_eq3=(_e("Drinking mate yeah"),
                  RAISES, ValueError),
        test_empty=(_e(""),
                  RAISES, ValueError),
        test_eq5=(_e("{Mate|thing**} {toilet|thing*}"),
                  EQ, set()),
    )

    @skip
    def test_fuzz(self):
        pass


class TestBagOfPosInBetween(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestBagOfWordBigramsInBetween(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass



class TestBagOfWordPosInBetween(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestBagOfWordPosBigramsInBetween(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestEntityOrder(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestEntityDistance(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass


class TestOtherEntitiesInBetween(TestCase, BaseFeatureFixture):
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

    @skip
    def test_fuzz(self):
        pass
