"""
Run IEPY rule-based extractor

Usage:
    iepy_rules_runner.py
    iepy_rules_runner.py -h | --help | --version

Picks from rules.py the relation to work with, and the rules definitions and
proceeds with the extraction.

Options:
  -h --help             Show this screen
  --version             Version number
"""
import sys
import logging

from django.core.exceptions import ObjectDoesNotExist

import iepy
iepy.setup(__file__)

from iepy.extraction.rules import load_rules
from iepy.extraction.rules_core import RuleBasedCore
from iepy.data import models, output
from iepy.data.db import CandidateEvidenceManager


def run_from_command_line():
    logging.basicConfig(level=logging.INFO, format='%(message)s')

    try:
        relation_name = iepy.instance.rules.RELATION
    except AttributeError:
        logging.error("RELATION not defined in rules file")
        sys.exit(1)

    try:
        relation = models.Relation.objects.get(name=relation_name)
    except ObjectDoesNotExist:
        logging.error("Relation {!r} not found".format(relation_name))
        sys.exit(1)

    # Load rules
    rules = load_rules()

    # Load evidences
    evidences = CandidateEvidenceManager.candidates_for_relation(relation)

    # Run the pipeline
    iextractor = RuleBasedCore(relation, rules)
    iextractor.start()
    iextractor.process()
    predictions = iextractor.predict(evidences)
    output.dump_output_loop(predictions)


if __name__ == u'__main__':
    run_from_command_line()
