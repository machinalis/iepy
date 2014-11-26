"""
IEPY gazettes loader

Usage:
    gazettes_loader.py <filename>
    gazettes_loader.py --freebase_type=<freebase_type> <KIND>


The <filename> argument can be a .csv file or a .csv.gz file containing the
gazettes in two columns: 'literal' and 'class'.


Options:
  -h --help             Show this screen
"""

import sys
import csv
import gzip
import logging
from operator import itemgetter

from django.db import IntegrityError
from docopt import docopt

import iepy
iepy.setup(__file__)
from iepy.data.models import EntityKind, GazetteItem
from iepy.preprocess.ner.literal import download_freebase_type

logging.basicConfig(level=logging.INFO, format='%(message)s')


def add_gazettes_from_csv(filepath):
    if filepath.endswith(".gz"):
        fin = gzip.open(filepath, "rt")
    else:
        fin = open(filepath, "rt")
    reader = csv.DictReader(fin)

    expected_fnames = ['literal', 'class']
    if not set(reader.fieldnames).issuperset(expected_fnames):
        msg = "Couldn't find the expected field names on the provided csv: {}"
        sys.exit(msg.format(expected_fnames))

    _create_gazette_entries(
        itemgetter(*expected_fnames)(line) for line in reader
    )


def _create_gazette_entries(entries_list, from_freebase=None):
    kind_cache = {}
    created = 0
    for literal, kind_name in entries_list:
        literal = literal.strip()
        kind_name = kind_name.strip()
        kind = kind_cache.get(kind_name)
        if kind is None:
            kind, _ = EntityKind.objects.get_or_create(name=kind_name)
            kind_cache[kind_name] = kind
        gazette = GazetteItem(text=literal, kind=kind)
        if from_freebase:
            gazette.from_freebase = from_freebase

        try:
            gazette.save()
        except IntegrityError as error:
            logging.warn(
                "Gazette '{}' of class '{}' not loaded, literal already existed".format(
                literal, kind_name))
            print(error)
        finally:
            created += 1
    print('Created {} new gazette items'.format(created))


if __name__ == "__main__":
    opts = docopt(__doc__, version=iepy.__version__)
    fname = opts["<filename>"]
    if fname:
        add_gazettes_from_csv(fname)
    else:
        kind = opts['<KIND>']
        freebase_type = opts['--freebase_type']
        gazettes = download_freebase_type(freebase_type)
        print('Downloaded {} entries from freebase. Uploading to database...')
        _create_gazette_entries(zip(gazettes, [kind]*len(gazettes)), freebase_type)
