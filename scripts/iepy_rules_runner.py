"""
Run IEPY core loop using rules

Usage:
    iepy_runner.py <rules_module>

Options:
  -h --help             Show this screen
  --version             Version number
"""

import logging
from docopt import docopt
from importlib import import_module

from iepy.extraction.rules_core import RulesBasedCore
from iepy.data import models
from iepy.data.db import CandidateEvidenceManager


if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    rules_module = opts['<rules_module>']

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Load module
    rules_module = import_module(rules_module)

    # Load relation
    if not hasattr(rules_module, "RELATION"):
        raise ValueError("Rules module does not define the RELATION attribute")
    relation = models.Relation.objects.get(name=rules_module.RELATION)

    # Load rules
    rules = []
    for attr_name in dir(rules_module):
        attr = getattr(rules_module, attr_name)
        if hasattr(attr, '__call__'):  # is callable
            if hasattr(attr, "is_rule") and attr.is_rule:
                rules.append(attr)

    # Load evidences
    evidences = CandidateEvidenceManager.candidates_for_relation(relation)

    # Run the pipeline
    iextractor = RulesBasedCore(relation, evidences, rules)
    iextractor.start()
    facts = iextractor.known_facts()
    print(facts)
