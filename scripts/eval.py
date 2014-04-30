"""
IEPY's result evaluator w.r.t. a reference corpus.

Usage:
    eval.py <dbname> <proposed_csv> <reference_csv>
    eval.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt

from iepy.db import connect
from iepy.utils import load_evidence_from_csv


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connector = connect(opts['<dbname>'])
    proposed_csv = opts['<proposed_csv>']
    reference_csv = opts['<reference_csv>']

    proposed = load_evidence_from_csv(proposed_csv, connector)
    reference = load_evidence_from_csv(reference_csv, connector)

    # ignore proposed facts with no evidence:
    proposed_positives = set([p for p in proposed.keys() if p.segment])
    reference_positives = set([p for p, b in reference.items() if b])
    coincident_positives = proposed_positives & reference_positives

    precision = float(len(coincident_positives)) / len(proposed_positives)
    recall = float(len(coincident_positives)) / len(reference_positives)

    print("Precision: %.2f" % precision)
    print("Recall: %.2f" % recall)

