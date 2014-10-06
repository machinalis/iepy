# -*- coding: utf-8 -*-

from unittest import mock
from .manager_case import ManagerTestCase

from refo import Question, Star, Any, Plus
from iepy.rules import BaseRule, Token, Kind
from iepy.extraction.rules_core import RulesBasedIEPipeline
from .factories import (
    EntityKindFactory, RelationFactory, TextSegmentFactory,
    IEDocFactory, EntityOccurrenceFactory, EntityFactory,
)


class TestRulesBasedIEPipeline(ManagerTestCase):

    def setUp(self):
        super(TestRulesBasedIEPipeline, self).setUp()

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

    def _create_simple_document(self, text):
        tokens = tuple(text.split())
        postags = ["POSTAG"] * len(tokens)
        indexes = tuple(list(range(len(tokens))))
        document = IEDocFactory(text=text)
        document.set_tokenization_result(list(zip(indexes, tokens)))
        document.set_tagging_result(postags)
        document.save()
        return document

    def test_rule_that_matches(self):
        class TestRule(BaseRule):
            relation = "born in"
            regex = Plus(Kind("person")) + Token("(") + Plus(Kind("date")) + \
                Token("-") + Question(Star(Any()))

        relation_rules = {self.person_date_relation: [TestRule]}
        pipeline = RulesBasedIEPipeline(relation_rules)
        pipeline.start()
        facts = pipeline.known_facts()

        relations = facts.keys()
        self.assertEqual(set(relations), set([self.person_date_relation]))
        self.assertEqual(len(facts[self.person_date_relation]), 1)
        evidence = facts[self.person_date_relation][0]
        self.assertEqual(evidence.segment.pk, self.segment.pk)

    def test_rule_that_not_matches(self):
        class TestRule(BaseRule):
            relation = "born in"
            regex = Token("something here")

        relation_rules = {self.person_date_relation: [TestRule]}
        pipeline = RulesBasedIEPipeline(relation_rules)
        pipeline.start()
        facts = pipeline.known_facts()

        relations = facts.keys()
        self.assertEqual(set(relations), set([self.person_date_relation]))
        self.assertEqual(len(facts[self.person_date_relation]), 0)

    def test_empty_rules(self):
        relation_rules = {}
        pipeline = RulesBasedIEPipeline(relation_rules)
        pipeline.start()
        facts = pipeline.known_facts()

        relations = facts.keys()
        self.assertEqual(set(relations), set())

    def test_get_rich_tokens_cleaned(self):
        evidences = list(self.segment.get_labeled_evidences(
            self.person_date_relation
        ))
        error_msg = "found none or more than one evidences for test segment"
        assert len(evidences) == 1, error_msg
        evidence = evidences[0]

        relation_rules = {}
        pipeline = RulesBasedIEPipeline(relation_rules)
        tokens = pipeline.get_rich_tokens_cleaned(evidence)

        lid = evidence.left_entity_occurrence.entity.id
        rid = evidence.right_entity_occurrence.entity.id

        for token in tokens:
            if token.eo_ids:
                self.assertTrue(lid in token.eo_ids or rid in token.eo_ids)

    def test_match_run_on_every_rule(self):
        mocked_rules = [mock.MagicMock()] * 10
        relation_rules = {self.person_date_relation: mocked_rules}
        pipeline = RulesBasedIEPipeline(relation_rules)
        pipeline.start()

        for mock_rule in mocked_rules:
            rule_inst = mock_rule()
            self.assertTrue(rule_inst.match.called)
