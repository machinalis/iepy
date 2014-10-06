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
            evidence.hydrate()
            enriched_tokens = evidence.get_enriched_tokens()
            for matched_relation in self.match(enriched_tokens):
                self.learnt[matched_relation].append(evidence)

    def known_facts(self):
        return self.learnt

    ###
    ### IEPY Internal Rules methods
    ###

    def match(self, evidence):
        result = []
        for rel, rules in self.relations_rules.items():
            for rule in rules:
                if rule.match(evidence):
                    result.append(rel)
                    break
        return result
