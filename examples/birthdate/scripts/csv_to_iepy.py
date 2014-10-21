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
import csv
import gzip
import os

from docopt import docopt

from iepy.data.db import DocumentManager


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    opts = docopt(__doc__, version=0.1)

    name = opts["<filename>"]
    if name.endswith(".gz"):
        fin = gzip.open(name, "rt")
    else:
        fin = open(name, "rt")
    reader = csv.DictReader(fin)
    name = os.path.basename(name)

    docdb = DocumentManager()

    seen = set()
    for i, d in enumerate(reader):
        mid = d["freebase_mid"]
        if mid in seen:
            continue
        seen.add(mid)
        docdb.create_document(identifier=mid,
                              text=d["description"],
                              metadata={"input_filename": name})
