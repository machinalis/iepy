"""
Run IEPY core loop using rules

Usage:
    iepy_runner.py <rules_module> <output_file>

Options:
  -h --help             Show this screen
  --version             Version number
"""

import logging
import inspect
from docopt import docopt
from collections import defaultdict
from importlib import import_module

from iepy.core_rules import RulesBasedIEPipeline
from iepy.data import models
from iepy import rules


if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    output_file = opts['<output_file>']
    rules_module = opts['<rules_module>']

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    rules_module = import_module(rules_module)
    relation_rules = defaultdict(list)

    for attr_name in dir(rules_module):
        attr = getattr(rules_module, attr_name)
        if inspect.isclass(attr) and issubclass(attr, rules.BaseRule):
            if attr.relation:
                relation = models.Relation.objects.get(name=attr.relation)
                # TODO: handle object not found
                relation_rules[relation].append(attr)

    pipeline = RulesBasedIEPipeline(relation_rules)
    pipeline.start()
    facts = pipeline.known_facts()
    print(facts)
    #facts.save_to_csv(output_file)
