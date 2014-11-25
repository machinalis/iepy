"""
IEPY gazettes loader

Usage:
    gazettes_loader.py <filename>

The <filename> argument can be a .csv file or a .csv.gz file containing the
gazettes in two columns: 'literal' and 'class'.

Options:
  -h --help             Show this screen
"""

import sys
import csv
import gzip
import logging
from docopt import docopt

from django.db import IntegrityError

import iepy
iepy.setup(__file__)
from iepy.data.models import EntityKind, GazetteItem

logging.basicConfig(level=logging.INFO, format='%(message)s')


def add_gazettes_from_csv(filepath):
    if filepath.endswith(".gz"):
        fin = gzip.open(filepath, "rt")
    else:
        fin = open(filepath, "rt")
    reader = csv.DictReader(fin)

    expected_fnames = ['literal', 'class']
    if not set(reader.fieldnames).issuperset(expected_fnames):
        msg = "Couldn't find the expected field names on the provided csv {}"
        sys.exit(msg.format(expected_fnames))

    kind_cache = {}
    for line in reader:
        kind = kind_cache.get(line["class"])
        if kind is None:
            kind, _ = EntityKind.objects.get_or_create(name=line["class"])
            kind_cache[line["class"]] = kind
        gazette = GazetteItem(
            text=line["literal"],
            kind=kind
        )

        try:
            gazette.save()
        except IntegrityError:
            logging.warn("Gazette '{}' of class '{}' not loaded, literal already existed".format(
                line["literal"], line["class"]
            ))


if __name__ == "__main__":
    opts = docopt(__doc__, version=iepy.__version__)
    add_gazettes_from_csv(opts["<filename>"])

