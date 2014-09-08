"""
IEPY's reference corpus generation utility.

Usage:
    generate_reference_corpus.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename> [options]
    generate_reference_corpus.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  -o --override         Discard previous data of the <output_filename>. If not provided, loads data <output_filename> and reuse the answers.
"""
from docopt import docopt

from iepy.data.db import connect
from iepy.data.knowledge import Knowledge
from iepy.human_validation import human_oracle


if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    connector = connect(opts[u'<dbname>'])

    relation_name = opts[u'<relation_name>']
    kind_a = opts[u'<kind_a>']
    kind_b = opts[u'<kind_b>']
    output_filename = opts[u'<output_filename>']

    if opts[u'--override']:
        kn = Knowledge()
    else:
        try:
            kn = Knowledge.load_from_csv(output_filename)
        except IOError:  # File does not exist
            kn = Knowledge()

    kn.extend_from_oracle(kind_a, kind_b, relation_name, human_oracle)
    kn.save_to_csv(output_filename)
