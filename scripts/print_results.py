"""
Print IEPY's results

Usage:
    print_results.py <dbname> <csv_file>
    print_results.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt
import logging

from iepy.core import BootstrappedIEPipeline
from iepy import db
from iepy.utils import load_evidence_from_csv


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connection = db.connect(opts['<dbname>'])
    csv_file = opts['<csv_file>']
    evidence = load_evidence_from_csv(csv_file, connection)
    
    for e in evidence:
        fact = e.colored_fact()
        print(u'FACT: {}'.format(fact))
        if e.segment:
            text = e.colored_text()
            print(u'  SEGMENT: {}'.format(text))

