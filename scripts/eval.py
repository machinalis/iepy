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
from iepy.knowledge import Knowledge
from iepy.utils import evaluate


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connector = connect(opts['<dbname>'])
    proposed_csv = opts['<proposed_csv>']
    reference_csv = opts['<reference_csv>']

    proposed = Knowledge.load_from_csv(proposed_csv)
    reference = Knowledge.load_from_csv(reference_csv)
    result = evaluate(proposed, reference)

    print("Precision: %.2f" % result['precision'])
    print("Recall: %.2f" % result['recall'])
