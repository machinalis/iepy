from getpass import getuser
import csv
import gzip
import logging
import os
import sys
import tarfile
import zipfile

import wget
from appdirs import AppDirs


logger = logging.getLogger(__name__)

DIRS = AppDirs('iepy', getuser())
if not os.path.exists(DIRS.user_data_dir):
    # making sure that user_data_dir exists
    os.mkdir(DIRS.user_data_dir)


def unzip(zipped_list, n):
    """returns n lists with the elems of zipped_list unsplitted.
    The general case could be solved with zip(*zipped_list), but here we
    are also dealing with:
      - un-zipping empy list to n empty lists
      - ensuring that all zipped items in zipped_list have lenght n, raising
        ValueError if not.
    """
    if not zipped_list:
        return tuple([[]] * n)
    else:
        if not all(isinstance(x, tuple) and len(x) == n for x in zipped_list):
            raise ValueError
        return zip(*zipped_list)


def unzip_from_url(zip_url, extraction_base_path):
    got_zipfile = None
    try:
        got_zipfile = wget.download(zip_url)
        print('')  # just because wget progress-bar finishes a line with no EOL
        unzip_file(got_zipfile, extraction_base_path)
    finally:
        if zipfile:
            os.remove(got_zipfile)


def unzip_file(zip_path, extraction_base_path):
    if zip_path.endswith('.tar.gz'):
        with tarfile.open(zip_path, mode='r:gz') as tfile:
            tfile.extractall(extraction_base_path)
    else:
        zfile = zipfile.ZipFile(zip_path)
        zfile.extractall(extraction_base_path)


def make_feature_list(text):
    return [x.strip() for x in text.split("\n") if x.strip()]


def evaluate(predicted_knowledge, gold_knowledge):
    """Computes evaluation metrics for a predicted knowledge with respect to a
    gold (or reference) knowledge. Returns a dictionary with the results.
    """
    # ignore predicted facts with no evidence:
    predicted_positives = set([p for p in predicted_knowledge.keys() if p.segment])
    gold_positives = set([p for p, b in gold_knowledge.items() if b])
    correct_positives = predicted_positives & gold_positives

    result = {}
    result['correct'] = correct = len(correct_positives)
    result['predicted'] = predicted = len(predicted_positives)
    result['gold'] = gold = len(gold_positives)

    if predicted > 0:
        result['precision'] = precision = float(correct) / predicted
    else:
        result['precision'] = precision = 1.0
    if gold > 0:
        result['recall'] = recall = float(correct) / gold
    else:
        result['recall'] = recall = 1.0
    if precision + recall > 0.0:
        result['f1'] = 2 * precision * recall / (precision + recall)
    else:
        result['f1'] = 0.0

    return result


def csv_to_iepy(filepath):
    print ('Importing Documents to IEPY from {}'.format(filepath))
    from iepy.data.db import DocumentManager

    if filepath.endswith(".gz"):
        fin = gzip.open(filepath, "rt")
    else:
        fin = open(filepath, "rt")
    reader = csv.DictReader(fin)

    expected_fnames = ['document_id', 'document_text']
    if not set(reader.fieldnames).issuperset(expected_fnames):
        msg = "Couldn't find the expected field names on the provided csv {}"
        sys.exit(msg.format(expected_fnames))

    name = os.path.basename(filepath)

    docdb = DocumentManager()
    seen = set()

    i = 0
    while True:

        try:
            d = next(reader)
        except StopIteration:
            break
        except csv.Error as error:
            logger.warn("Couldn't load document: {}".format(error))
            continue

        i += 1

        doc_id = d["document_id"]
        if doc_id in seen:
            continue
        seen.add(doc_id)
        docdb.create_document(
            identifier=doc_id,
            text=d["document_text"],
            metadata={"input_filename": name},
            update_mode=True
        )
        print ('Added {} documents'.format(i))
