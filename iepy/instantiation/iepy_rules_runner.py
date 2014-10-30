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

from docopt import docopt

import iepy
iepy.setup(__file__)

from iepy.extraction.rules_core import RuleBasedCore
from iepy.data import models, output
from iepy.data.db import CandidateEvidenceManager

import rules


if __name__ == u'__main__':
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    opts = docopt(__doc__, version=iepy.__version__)

    try:
        relation = rules.RELATION
    except AttributeError:
        logging.error("RELATION not defined in rules file")
        sys.exit(1)

    relation = models.Relation.objects.get(name=rules.RELATION)

    # Load rules
    rules = []
    for attr_name in dir(rules):
        attr = getattr(rules, attr_name)
        if hasattr(attr, '__call__'):  # is callable
            if hasattr(attr, "is_rule") and attr.is_rule:
                rules.append(attr)

    # Load evidences
    evidences = CandidateEvidenceManager.candidates_for_relation(relation)

    # Run the pipeline
    iextractor = RuleBasedCore(relation, evidences, rules)
    iextractor.start()
    iextractor.process()
    predictions = iextractor.predict()
    output.dump_output_loop(predictions)
