# -*- coding: utf-8 -*-
"""
Experimental evaluation of FactExtractor round 2.

Usage:
    factextractor_round2.py <relation_name>

Options:
 -h --help              Show this screen.
"""
from utils import apply_dict_combinations
from iepy.utils import make_feature_list


def iter_configs(relation_name):
    base = {
        # Experiment configuration
        "config_version": "2relationextractionclassifier",
        "data_shuffle_seed": "portishead",
        "train_size": None,
        #"relation": "was born",
        "relation": relation_name,

        # Classifier configuration
        "classifier": "svc",
        "classifier_args": dict(),
        "sparse_features": make_feature_list("""
            bag_of_words
            bag_of_pos
            bag_of_words_in_between
            bag_of_pos_in_between"""),
        "dense_features": make_feature_list("""
            entity_order
            entity_distance
            other_entities_in_between
            verbs_count_in_between
            verbs_count
            total_number_of_entities
            symbols_in_between
            number_of_tokens""")
    }

    patch = {"train_size": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100,
                            125, 150, 175, 200,
                            300, 500, 1000],
             "data_shuffle_seed": [base["data_shuffle_seed"] + str(i) for i in range(10)]}

    for config in apply_dict_combinations(base, patch):
        yield config


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.DEBUG)
    opts = docopt(__doc__)
    relation_name = opts["<relation_name>"]

    configs = list(iter_configs(relation_name))

    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
