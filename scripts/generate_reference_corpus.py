"""
IEPY's reference corpus generation utility.

Usage:
    generate_reference_corpus.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename> [options]
    generate_reference_corpus.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  -c --continue         Load output filename and reuse the answers.
"""
from docopt import docopt

from iepy.db import connect
from iepy.data_generation import label_evidence_from_oracle
from iepy.human_validation import human_oracle
from iepy.utils import save_labeled_evidence_to_csv, load_evidence_from_csv


class CombinedOracle(object):

    def __init__(self, knowledge, relation):
        self.knowledge = knowledge
        self.relation = relation

    def __call__(self, evidence):
        if evidence in self.knowledge:
            answer = self.knowledge[evidence]
            assert answer in [0, 1]
            if answer == 0:
                return 'n'
            else:
                return 'y'
        else:
            return human_oracle(evidence)


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connector = connect(opts['<dbname>'])

    relation_name = opts['<relation_name>']
    kind_a = opts['<kind_a>']
    kind_b = opts['<kind_b>']
    output_filename = opts['<output_filename>']
    cont = opts['--continue']

    if cont:
        knowledge = load_evidence_from_csv(output_filename, connector)
        oracle = CombinedOracle(knowledge, relation_name)
    else:
        oracle = human_oracle

    r = label_evidence_from_oracle(kind_a, kind_b, relation_name, oracle)
    save_labeled_evidence_to_csv(r, output_filename)
