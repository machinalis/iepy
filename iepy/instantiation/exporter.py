"""
Run IEPY exporters

Usage:
    exporter.py brat-format <output-folder> [options]
    exporter.py -h | --help | --version

Options:
  --relations=<r-names>     Names of relations to export. May be more than one,
                            comma separated.
  --version                 Version number
  -h --help                 Show this screen
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


def _get_relations(opts):
    k = '--relations'
    result = []
    if k not in opts:
        return result
    relation_names = opts.get(k).split(',')
    for r_name in relation_names:
        try:
            result.append(Relation.objects.get(name=r_name))
        except Relation.DoesNotExist:
            print("Relation {!r} non existent".format(r_name))
            print_all_relations()
            exit(1)
    return result


def run_from_command_line():
    opts = docopt(__doc__, version=iepy.__version__)

    logging.basicConfig(level=logging.INFO, format='%(message)s')
    logging.getLogger("featureforge").setLevel(logging.WARN)

    if 'brat-format' in opts:
        exporter = Brat()
        relations = _get_relations(opts)
        docs = DocumentManager().get_preprocessed_documents()
        exporter.run(opts['<output-folder>'], docs, relations)


if __name__ == u'__main__':
    run_from_command_line()
