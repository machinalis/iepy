# -*- coding: utf-8 -*-

import refo
from unittest import skip, mock

from featureforge.validate import BaseFeatureFixture, EQ
from featureforge.feature import make_feature

from iepy.data.db import CandidateEvidenceManager
from iepy.extraction import features
from iepy.extraction.rules import rule
from iepy.extraction.features import (
    bag_of_words, bag_of_pos, bag_of_word_bigrams, bag_of_wordpos,
    bag_of_wordpos_bigrams, bag_of_words_in_between, bag_of_pos_in_between,
    bag_of_word_bigrams_in_between, bag_of_wordpos_in_between,
    bag_of_wordpos_bigrams_in_between, entity_order, entity_distance,
    other_entities_in_between, total_number_of_entities,
    verbs_count_in_between, verbs_count, symbols_in_between,
    parse_features
)

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

class MockedModule:
    def custom_feature(*args, **kwargs):
        return "custom feature"

    @rule(True)
    def custom_rule_feature(*args, **kwargs):
        return refo.Star(refo.Any())

    @rule(False)
    def custom_negative_rule_feature(*args, **kwargs):
        return refo.Star(refo.Any())


class TestCustomFeatures(ManagerTestCase):
    def test_parse_custom_feature(self):
        with mock.patch("importlib.import_module") as mock_import:
            mocked_module = MockedModule()
            mock_import.return_value = mocked_module
            fs = parse_features(["app.module.custom_feature"])
            mock_import.assert_called_with("app.module")

            self.assertEqual(len(fs), 1)
            self.assertEqual(fs[0](), "custom feature")

    def test_parse_custom_rule_feature(self):
        with mock.patch("importlib.import_module") as mock_import:
            with mock.patch.object(features, "rule_wrapper") as mock_rule_wrapper:
                mocked_module = MockedModule()
                mock_import.return_value = mocked_module
                fs = parse_features(["app.rules.custom_rule_feature"])
                mock_import.assert_called_with("app.rules")
                self.assertEqual(len(fs), 1)
                self.assertTrue(mock_rule_wrapper.called)

    def test_invalid_custom_feature(self):
        with self.assertRaises(KeyError):
            parse_features(["does.not.exists"])

    def test_rule_wrapper_returns_int(self):
        with mock.patch("importlib.import_module") as mock_import:
            mocked_module = MockedModule()
            mock_import.return_value = mocked_module
            evidence = _e("test")

            fs = parse_features(["app.rules.custom_rule_feature"])
            self.assertEqual(fs[0](evidence), 1)

            fs = parse_features(["app.rules.custom_negative_rule_feature"])
            self.assertEqual(fs[0](evidence), 0)
