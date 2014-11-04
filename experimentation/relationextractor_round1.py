# -*- coding: utf-8 -*-
"""
Experimental evaluation of FactExtractor round 1.

Usage:
    factextractor_round1.py

Options:
 -h --help              Show this screen.
"""
from utils import apply_dict_combinations, check_configs
from iepy.utils import make_feature_list


def iter_configs():
    base = {
        # Experiment configuration
        "config_version": "2relationextractionclassifier",
        "data_shuffle_seed": "flume",
        "train_size": None,
        "relation": "was born",

        # Classifier configuration
        "classifier": None,
        "classifier_args": dict(),
        "sparse_features": None,
        "dense_features": None
    }

    bowfeats = make_feature_list("""
                bag_of_words
                bag_of_pos
                bag_of_words_in_between
                bag_of_pos_in_between""")
    densefeats = make_feature_list("""
                entity_order
                entity_distance
                other_entities_in_between
                in_same_sentence
                verbs_count_in_between
                verbs_count
                total_number_of_entities
                symbols_in_between
                number_of_tokens""")

    base["sparse_features"] = bowfeats
    base["dense_features"] = densefeats

    patch = {"train_size": [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000],
             "data_shuffle_seed": [base["data_shuffle_seed"] + str(i) for i in range(10)]}

    xs = "sgd svc knn randomforest adaboost".split()
    for classifier in xs:
        base["classifier"] = classifier
        for config in apply_dict_combinations(base, patch):
            yield config


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.DEBUG)
    configs = list(iter_configs())

    opts = docopt(__doc__)
    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
