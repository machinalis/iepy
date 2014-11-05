# -*- coding: utf-8 -*-

from operator import attrgetter
import logging

import refo

from iepy.extraction.rules import generate_subject_and_object, generate_tokens_to_match, _EOL

logger = logging.getLogger(__name__)


class RuleBasedCore(object):
    """
    IEPY's alternative main class. Implements a rule-based information extractor.

    From the user's point of view this class is meant to be used like this::

        extractor = RuleBasedCore(relation, evidences, [<rule-1>, ..., <rule-n>])
        extractor.start()
        predictions = extractor.predict()  # profit
    """
    def __init__(self, relation, evidences, rules):
        self.relation = relation
        self.rules = sorted(rules, key=attrgetter("priority"), reverse=True)
        self.evidences = evidences
        self.learnt = {}

    ###
    ### IEPY User API
    ###

    def start(self):
        """
        Prepares the internal information to start predicting.
        """
        # Right now it's a dumb method, here just because API compliance.
        # Anyways, it's a good placeholder for doing some heavy computations if you
        # need to.
        pass

    def predict(self):
        """
        Using the provided rules, on the given order, applies them to each evidence
        candidate, verifying if they match or not.
        Returns a dict {evidence: True/False}, where the boolean label indicates if
        the relation is present on that evidence or not.
        """
        logger.info('Predicting using rule based core')
        predicted = {}
        for evidence in self.evidences:
            match = self.match(evidence)
            predicted[evidence] = match if match is not None else False
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
        Subject, Object = generate_subject_and_object(evidence)
        tokens_to_match = generate_tokens_to_match(evidence)

        for rule in self.rules:
            regex = rule(Subject, Object) + refo.Literal(_EOL)

            match = refo.match(regex, tokens_to_match)
            if match:
                return rule.answer
