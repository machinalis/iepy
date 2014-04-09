# -*- coding: utf-8 -*-
from unittest import TestCase

from featureforge.validate import BaseFeatureFixture, EQ, IN, APPROX, RAISES

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
    evidence.segment.pos = pos
    return evidence


class TestBagOfWords(TestCase, BaseFeatureFixture):
    feature = bag_of_words
    fixtures = dict(
        test_eq=(_e("Drinking {Mate|thing*} makes you go to the {toilet|thing**}"),
                 EQ, set("drinking mate makes you go to the toilet".split()))
    )
