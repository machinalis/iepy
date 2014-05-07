"""
IEPY's seed generation utility.

Usage:
    generate_seeds.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename>
    generate_seeds.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt

from iepy.db import connect
from iepy.data_generation import label_evidence_from_oracle
from iepy.human_validation import human_oracle
from iepy.utils import save_facts_to_csv


if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    connect(opts[u'<dbname>'])

    relation_name = opts[u'<relation_name>']
    kind_a = opts[u'<kind_a>']
    kind_b = opts[u'<kind_b>']
    output_filename = opts[u'<output_filename>']

    r = label_evidence_from_oracle(kind_a, kind_b, relation_name, human_oracle)
    facts = [ev.fact for (ev, label) in r if label]
    save_facts_to_csv(facts, output_filename)
