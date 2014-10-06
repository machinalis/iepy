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

from iepy.data.db import connect
from iepy.data.knowledge import Knowledge
from iepy.extraction.human_validation import human_oracle
from iepy.utils import save_facts_to_csv


if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    connect(opts[u'<dbname>'])

    relation_name = opts[u'<relation_name>']
    kind_a = opts[u'<kind_a>']
    kind_b = opts[u'<kind_b>']
    output_filename = opts[u'<output_filename>']

    kn = Knowledge()
    kn.extend_from_oracle(kind_a, kind_b, relation_name, human_oracle)
    facts = set([ev.fact for (ev, value) in kn.items() if value == 1])
    save_facts_to_csv(sorted(facts), output_filename)
