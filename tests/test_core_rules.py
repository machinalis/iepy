# -*- coding: utf-8 -*-

from unittest import mock

from refo.patterns import Pattern
from refo import Question, Star, Any

from iepy.data.db import CandidateEvidenceManager
from iepy.extraction.rules import rule, Token
from iepy.extraction.rules_core import RuleBasedCore
from .factories import (
    EntityKindFactory, RelationFactory, TextSegmentFactory,
    IEDocFactory, EntityOccurrenceFactory, EntityFactory,
)
from .manager_case import ManagerTestCase


class TestRuleBasedCore(ManagerTestCase):

    def setUp(self):
        super(TestRuleBasedCore, self).setUp()

        kind_person = EntityKindFactory(name="person")
        kind_date = EntityKindFactory(name="date")
        self.person_date_relation = RelationFactory(
            name="born in",
            left_entity_kind=kind_person,
            right_entity_kind=kind_date,
        )
        text = "John Soplete ( 15 august 1990 - 26 september 2058 ) " \
               "was a software developer"
        document = self._create_simple_document(text)
        segment = TextSegmentFactory(
            document=document,
            offset=0,
            offset_end=len(document.tokens)
        )
        self.segment = segment
        e_john = EntityFactory(key="John Soplete", kind=kind_person)
        eo1 = EntityOccurrenceFactory(
            entity=e_john, document=document,
            offset=0, offset_end=2,
            alias="j0hn",
        )
        eo1.segments.add(segment)
        e_date = EntityFactory(key="15 august 1990", kind=kind_date)
        eo2 = EntityOccurrenceFactory(
            entity=e_date, document=document,
            offset=3, offset_end=6,
            alias="1990-08-15",
        )
        eo2.segments.add(segment)
        self._candidates = self.get_candidates(self.person_date_relation)

    def get_candidates(self, relation):
        return list(CandidateEvidenceManager.candidates_for_relation(relation))

    def _create_simple_document(self, text):
        tokens = tuple(text.split())
        lemmas = [""] * len(tokens)
        postags = ["POSTAG"] * len(tokens)
        indexes = tuple(list(range(len(tokens))))
        document = IEDocFactory(text=text)
        document.set_tokenization_result(list(zip(indexes, tokens)))
        document.set_lemmatization_result(lemmas)
        document.set_tagging_result(postags)
        document.save()
        return document

    def test_rule_that_matches(self):

        @rule(True)
        def test_rule(Subject, Object):
            anything = Question(Star(Any()))
            return Subject + Token("(") + Object + Token("-") + anything

        pipeline = RuleBasedCore(self.person_date_relation, [test_rule])
        pipeline.start()
        pipeline.process()
        facts = pipeline.predict(self._candidates)
        candidate = self._candidates[0]
        self.assertTrue(facts[candidate])

    def test_rule_that_not_matches(self):

        @rule(True)
        def test_rule(Subject, Object):
            return Subject + Object + Token("something here")

        pipeline = RuleBasedCore(self.person_date_relation, [test_rule])
        pipeline.start()
        pipeline.process()
        facts = pipeline.predict(self._candidates)
        candidate = self._candidates[0]
        self.assertFalse(facts[candidate])

    def test_empty_rules(self):
        pipeline = RuleBasedCore(self.person_date_relation, [])
        pipeline.start()
        pipeline.process()
        facts = pipeline.predict(self._candidates)
        self.assertEqual(len([x for x in facts if facts[x]]), 0)

    def test_match_run_on_every_rule(self):
        mocked_rules = [
            rule(True)(mock.MagicMock(return_value=Token("asd")))
        ] * 10
        pipeline = RuleBasedCore(self.person_date_relation, mocked_rules)
        pipeline.start()
        pipeline.process()
        pipeline.predict(self._candidates)

        for mock_rule in mocked_rules:
            self.assertTrue(mock_rule.called)
            Subject, Object = mock_rule.call_args[0]
            self.assertIsInstance(Subject, Pattern)

    def test_rule_priority(self):

        matcher = lambda *args: True
        not_matcher = lambda *args: None

        rule_should_run = rule(True, priority=1)(mock.MagicMock(return_value=matcher))
        rule_should_not_run = rule(True, priority=0)(
            mock.MagicMock(return_value=not_matcher))

        pipeline = RuleBasedCore(self.person_date_relation,
                                 [rule_should_not_run, rule_should_run])
        pipeline.start()
        # All rules are compiled on start
        self.assertTrue(rule_should_run.called)
        self.assertTrue(rule_should_not_run.called)
        pipeline.process()
        import refo
        with mock.patch.object(refo, 'match') as fake_refo_match:
            fake_refo_match.side_effect = lambda regex, evidence: regex()
            pipeline.predict(self._candidates)
            self.assertEqual(fake_refo_match.call_count, len(self._candidates))
            # check that on every call, the called is rule_match
            for c_args in fake_refo_match.call_args_list:
                args, kwargs = c_args
                self.assertEqual(args[0], matcher)

    def test_rule_incorrect_answer(self):
        with self.assertRaises(ValueError):
            @rule("YE")
            def rule_match(Subject, Object):
                anything = Question(Star(Any()))
                return Subject + Token("(") + Object + Token("-") + anything

    def test_rule_with_negative_answer(self):
        @rule(False)
        def test_rule(Subject, Object):
            anything = Question(Star(Any()))
            return Subject + Token("(") + Object + Token("-") + anything

        pipeline = RuleBasedCore(self.person_date_relation, [test_rule])
        pipeline.start()
        pipeline.process()
        facts = pipeline.predict(self._candidates)
        candidate = self._candidates[0]
        self.assertFalse(facts[candidate])
