# -*- coding: utf-8 -*-

from unittest import mock
from .manager_case import ManagerTestCase

from refo.patterns import Pattern
from refo import Question, Star, Any
from iepy.extraction.rules_core import RulesBasedIEPipeline, Token
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

        def test_rule(Subject, Object):
            anything = Question(Star(Any()))
            return Subject + Token("(") + Object + Token("-") + anything

        pipeline = RulesBasedIEPipeline(self.person_date_relation, [test_rule])
        pipeline.start()
        facts = pipeline.known_facts()

        self.assertEqual(len(facts), 1)
        evidence = facts[0]
        self.assertEqual(evidence.segment.id, self.segment.id)

    def test_rule_that_not_matches(self):

        def test_rule(Subject, Object):
            return Subject + Object + Token("something here")

        pipeline = RulesBasedIEPipeline(self.person_date_relation, [test_rule])
        pipeline.start()
        facts = pipeline.known_facts()
        self.assertEqual(len(facts), 0)

    def test_empty_rules(self):
        pipeline = RulesBasedIEPipeline(self.person_date_relation, [])
        pipeline.start()
        facts = pipeline.known_facts()
        self.assertEqual(len(facts), 0)

    def test_match_run_on_every_rule(self):
        mocked_rules = [mock.MagicMock(return_value=Token("asd"))] * 10
        pipeline = RulesBasedIEPipeline(self.person_date_relation, mocked_rules)
        pipeline.start()

        for mock_rule in mocked_rules:
            self.assertTrue(mock_rule.called)
            Subject, Object = mock_rule.call_args[0]
            self.assertIsInstance(Subject, Pattern)
