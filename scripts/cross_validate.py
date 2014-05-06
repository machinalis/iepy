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

import logging
import pprint
import sys

from docopt import docopt

from iepy import db
from iepy.fact_extractor import FactExtractorFactory
from iepy.knowledge import Knowledge
from iepy.utils import load_evidence_from_csv, make_feature_list

config = {
    "classifier": "svm",
    "classifier_args": dict(),
    "dimensionality_reduction": None,
    "dimensionality_reduction_dimension": None,
    "feature_selection": None,
    "feature_selection_dimension": None,
    "scaler": False,
    "sparse": True,
    "features": make_feature_list("""
            bag_of_words
            bag_of_pos
            bag_of_word_bigrams
            bag_of_wordpos
            bag_of_wordpos_bigrams
            bag_of_words_in_between
            bag_of_pos_in_between
            bag_of_word_bigrams_in_between
            bag_of_wordpos_in_between
            bag_of_wordpos_bigrams_in_between
            entity_order
            entity_distance
            other_entities_in_between
            in_same_sentence
            verbs_count_in_between
            verbs_count
            total_number_of_entities
            symbols_in_between
            number_of_tokens
            BagOfVerbStems True
            BagOfVerbStems False
            BagOfVerbLemmas True
            BagOfVerbLemmas False
    """),
}


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
