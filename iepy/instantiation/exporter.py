"""
Run IEPY exporters

Usage:
    exporter.py [options] <relation_name> <output>
    exporter.py -h | --help | --version

Options:
  --version                                Version number
  -h --help                                Show this screen
"""

import os
import json
import logging
from docopt import docopt
from sys import exit

import iepy
INSTANCE_PATH = iepy.setup(__file__)

from iepy.extraction.active_learning_core import ActiveLearningCore, HIPREC, HIREC
from iepy.data.db import CandidateEvidenceManager
from iepy.data.models import Relation
from iepy.extraction.terminal import TerminalAdministration
from iepy.data import output


def print_all_relations():
    print("All available relations:")
    for relation in Relation.objects.all():
        print("  {}".format(relation))


def load_labeled_evidences(relation, evidences):
    CEM = CandidateEvidenceManager  # shorcut
    return CEM.labels_for(relation, evidences, CEM.conflict_resolution_newest_wins)

def _get_relation(opts):
    relation_name = opts['<relation_name>']
    try:
        relation = Relation.objects.get(name=relation_name)
    except Relation.DoesNotExist:
        print("Relation {!r} non existent".format(relation_name))
        print_all_relations()
        exit(1)
    return relation


def run_from_command_line():
    opts = docopt(__doc__, version=iepy.__version__)

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.getLogger("featureforge").setLevel(logging.WARN)

    relation = _get_relation(opts)

    candidates = CandidateEvidenceManager.candidates_for_relation(relation)
    labeled_evidences = load_labeled_evidences(relation, candidates)

    for le in labeled_evidences:
        print (le)


if __name__ == u'__main__':
    run_from_command_line()
