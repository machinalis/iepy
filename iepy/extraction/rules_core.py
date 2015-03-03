# -*- coding: utf-8 -*-

from operator import attrgetter
import logging

import refo

from iepy.extraction.rules import generate_tokens_to_match, compile_rule

logger = logging.getLogger(__name__)


class RuleBasedCore(object):
    """
    IEPY's alternative main class. Implements a rule-based information extractor.

    From the user's point of view this class is meant to be used like this::

        extractor = RuleBasedCore(relation, [<rule-1>, ..., <rule-n>])
        extractor.start()
        predictions = extractor.predict(candidates)  # profit
    """
    def __init__(self, relation, rules, verbosity=0):
        self.relation = relation
        self.rules = sorted(rules, key=attrgetter("priority"), reverse=True)
        self.learnt = {}
        self.verbosity = verbosity

    ###
    ### IEPY User API
    ###

    def start(self):
        """
        Prepares the internal information to start predicting.
        """
        self.rule_regexes = [
            (compile_rule(rule, self.relation), rule.answer) for rule in self.rules
        ]

    def predict(self, candidates):
        """
        Using the provided rules, on the given order, applies them to each evidence
        candidate, verifying if they match or not.
        Returns a dict {evidence: True/False}, where the boolean label indicates if
        the relation is present on that evidence or not.
        """
        logger.info('Predicting using rule based core')
        predicted = {}
        for i, evidence in enumerate(candidates):
            match = self.match(evidence)
            predicted[evidence] = match if match is not None else False
            if self.verbosity > 0:
                if (i + 1) % 1000 == 0:
                    logger.info('checked {} candidate evidences'.format(i+1))
        return predicted

    def add_answer(self):
        """Dumb method on this extractor, just API compliance"""
        pass

    def process(self):
        """Dumb method on this extractor, just API compliance"""
        pass

    @property
    def questions(self):
        """Dumb method on this extractor, just API compliance"""
        return []

    def match(self, evidence):
        tokens_to_match = generate_tokens_to_match(evidence)
        for regex, answer in self.rule_regexes:
            match = refo.match(regex, tokens_to_match)
            if match:
                return answer
