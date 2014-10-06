# -*- coding: utf-8 -*-
import logging

logger = logging.getLogger(__name__)


class RulesBasedIEPipeline(object):
    def __init__(self, relations_rules):
        """
        relations_rules is a dict like this:
        {
            <relation_a>: [<rule 1>, <rule_2>, ...]
        }
        """
        self.relations_rules = relations_rules
        self.learnt = {}

    ###
    ### IEPY User API
    ###

    def start(self):
        logger.info('Starting rule based core')

        self.evidences = []
        for r in self.relations_rules.keys():
            for segment in r._matching_text_segments():
                self.evidences.extend(segment.get_labeled_evidences(r))
        self.learnt = {r: [] for r in self.relations_rules}

        for evidence in self.evidences:
            rich_tokens = self.get_rich_tokens_cleaned(evidence)
            for matched_relation in self.match(rich_tokens):
                self.learnt[matched_relation].append(evidence)

    def known_facts(self):
        return self.learnt

    ###
    ### IEPY Internal Rules methods
    ###

    def get_rich_tokens_cleaned(self, evidence):
        segment = evidence.segment
        segment.hydrate()
        rich_tokens = list(segment.get_enriched_tokens())

        # Clean tokens that are not in this evidence
        left_id = evidence.left_entity_occurrence.entity.id
        right_id = evidence.right_entity_occurrence.entity.id
        for token in rich_tokens:
            eo_ids = token.eo_ids
            eo_kinds = token.eo_kinds
            if eo_ids:
                if left_id not in eo_ids or right_id not in eo_ids:
                    eo_ids.clear()
                    eo_kinds.clear()

        return rich_tokens

    def match(self, evidence):
        result = []
        for rel, rules in self.relations_rules.items():
            for rule in rules:
                r = rule()
                if r.match(evidence):
                    result.append(rel)
                    break
        return result
