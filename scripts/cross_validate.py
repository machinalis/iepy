#!/usr/bin/env python
"""
Cross-validate IEPY classifier

Usage:
    cross_validate.py [--k=<subsamples>] <dbname> <gold_standard>
    cross_validate.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  --k=<subsamples>      Number of subsamples [default: 10]
"""
from __future__ import division

import codecs
import csv
import logging
import pprint
import sys

from docopt import docopt

from iepy import db
from iepy.core import Knowledge, Fact, Evidence
from iepy.fact_extractor import FactExtractorFactory

config = {
    "classifier": "dtree",
    "classifier_args": dict(),
    "dimensionality_reduction": None,
}


def load_evidence_from_csv(filename, connection):
    result = Knowledge()
    with codecs.open(filename, encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            entity_a = db.get_entity(row[0], row[1])
            entity_b = db.get_entity(row[2], row[3])
            f = Fact(entity_a, row[4], entity_b)
            s = db.get_segment(row[5], int(row[6]))
            e = Evidence(fact=f, segment=s, o1=int(row[7]), o2=int(row[8]))
            assert s.entities[e.o1].key == entity_a.key
            assert s.entities[e.o2].key == entity_b.key
            result[e] = int(row[9] == "True")
    return result


def main(options):
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    connection = db.connect(options['<dbname>'])
    standard = load_evidence_from_csv(options['<gold_standard>'], connection)
    logging.info("Loaded %d samples from gold standard", len(standard))
    k = int(options['--k'])

    success = total = 0
    confusion_matrix = [[[], []], [[], []]]
    logging.info("Splitting into %d subsamples", k)
    for subsample in range(k):
        logging.debug("Subsample = %d", subsample)
        train_data = Knowledge()
        test_data = []
        test_labels = []
        for i, (e, s) in enumerate(standard.items()):
            if i % k == subsample:
                test_data.append(e)
                test_labels.append(s)
            else:
                train_data[e] = s
        extractor = FactExtractorFactory(config, train_data)
        prediction = extractor.predict(test_data)
        assert len(prediction) == len(test_data)
        total += len(prediction)
        success += sum(1 for (p, e) in zip(prediction, test_labels) if p == e)
        for i, (p, e) in enumerate(zip(prediction, test_labels)):
            confusion_matrix[p][e].append(test_data[i])
    logging.info("%d values evaluated;", total)
    logging.info("%d accurate predictions (%d negative, %d positive)", success, len(confusion_matrix[0][0]), len(confusion_matrix[1][1]))
    logging.info("%d inaccurate predictions (%d actual positive, %d actual negative)", total-success, len(confusion_matrix[0][1]), len(confusion_matrix[1][0]))
    for e in confusion_matrix[0][1][:3]:
        logging.info("Predicted negative, actually positive: %s", e)
    for e in confusion_matrix[1][0][:3]:
        logging.info("Predicted positive, actually negative: %s", e)

    try:
        precision = len(confusion_matrix[1][1]) / len(confusion_matrix[1][0]+confusion_matrix[1][1])
    except ZeroDivisionError:
        precision = None
    try:
        recall = len(confusion_matrix[1][1]) / len(confusion_matrix[0][1]+confusion_matrix[1][1])
    except ZeroDivisionError:
        recall = None
    accuracy = success / total
    return accuracy, precision, recall


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    accuracy, precision, recall = main(opts)
    pprint.pprint(config)
    print("Accuracy: %.2f" % accuracy)
    print("Precision: %.2f" % precision)
    print("Recall: %.2f" % recall)
