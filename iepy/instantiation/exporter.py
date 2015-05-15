"""
Run IEPY exporters

Usage:
    exporter.py brat-format <relation_name> <output-folder>
    exporter.py -h | --help | --version

Options:
  --version                                Version number
  -h --help                                Show this screen
"""

import logging
from docopt import docopt
from sys import exit

import iepy
INSTANCE_PATH = iepy.setup(__file__)

from iepy.data.db import DocumentManager, CandidateEvidenceManager
from iepy.data.models import Relation
from iepy.data.export import Brat


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
    if 'brat-format' in opts:
        Brat().run(opts['<output-folder>'],
                   DocumentManager().get_preprocessed_documents()[:10])

if __name__ == u'__main__':
    run_from_command_line()
