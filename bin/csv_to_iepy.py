"""
Birthdate corpus preprocessing script.

Usage:
    csv_to_iepy.py <filename>
    csv_to_iepy.py -h | --help

The <filename> argument can be a .csv file or a .csv.gz file containing the
corpus in two columns: 'freebase_mid' and 'description'.

Options:
  -h --help             Show this screen
"""

import logging

from docopt import docopt

from iepy.utils import csv_to_iepy

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    opts = docopt(__doc__, version=0.1)
    filepath = opts["<filename>"]
    csv_to_iepy(filepath)
