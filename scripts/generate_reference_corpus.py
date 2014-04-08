"""
IEPY's reference corpus generation utility.

Usage:
    generate_reference_corpus.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename>
    generate_reference_corpus.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt

from iepy.db import connect
from scripts.generate_seeds import label_evidence_from_oracle, human_oracle
from iepy.utils import save_labeled_evidence_to_csv


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])

    relation_name = opts['<relation_name>']
    kind_a = opts['<kind_a>']
    kind_b = opts['<kind_b>']
    output_filename= opts['<output_filename>']

    r = label_evidence_from_oracle(kind_a, kind_b, human_oracle)
    # insert relation name:
    r2 = [(s, e1, e2, relation_name, label) for (s, e1, e2, label) in r]
    save_labeled_evidence_to_csv(r2, output_filename)

