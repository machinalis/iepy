from getpass import getuser
import os
import csv
import gzip
import zipfile

from appdirs import AppDirs


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


def unzip_file(zip_path, extraction_base_path):
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
    from iepy.data.db import DocumentManager

    if filepath.endswith(".gz"):
        fin = gzip.open(filepath, "rt")
    else:
        fin = open(filepath, "rt")
    reader = csv.DictReader(fin)
    name = os.path.basename(filepath)

    docdb = DocumentManager()
    seen = set()
    for i, d in enumerate(reader):
        mid = d["freebase_mid"]
        if mid in seen:
            continue
        seen.add(mid)
        docdb.create_document(
            identifier=mid,
            text=d["description"],
            metadata={"input_filename": name}
        )
