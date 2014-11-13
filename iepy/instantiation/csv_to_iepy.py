"""
IEPY database loader from csv file

Usage:
    csv_to_iepy.py <filename>
    csv_to_iepy.py -h | --help

The <filename> argument can be a .csv file or a .csv.gz file containing the
corpus in two columns: 'freebase_mid' and 'description'.

Options:
  -h --help             Show this screen
  --version             Version number
"""

import logging

from docopt import docopt

import iepy
iepy.setup(__file__)
from iepy.utils import csv_to_iepy

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(message)s')
    opts = docopt(__doc__, version=iepy.__version__)
    filepath = opts["<filename>"]
    csv_to_iepy(filepath)
