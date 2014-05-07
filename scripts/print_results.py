"""
IEPY's result pretty printer.

Usage:
    print_results.py <dbname> <csv_file>
    print_results.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt

from iepy import db
from iepy.knowledge import Knowledge


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connection = db.connect(opts['<dbname>'])
    csv_file = opts['<csv_file>']
    evidence = Knowledge.load_from_csv(csv_file)

    for e in evidence:
        fact = e.colored_fact()
        print(u'FACT: {}'.format(fact))
        if e.segment:
            text = e.colored_text()
            print(u'  SEGMENT: {}'.format(text))
