import os
import logging

import iepy
here = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(here)
iepy.setup(parent_dir)

from iepy.extraction.rules_core import RulesBasedCore
from iepy.data import models
from iepy.data.db import CandidateEvidenceManager

import rules


if __name__ == u'__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

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
    iextractor = RulesBasedCore(relation, evidences, rules)
    iextractor.start()
    facts = iextractor.known_facts()
    print(facts)
