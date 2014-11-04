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
        "config_version": "2active_learning",
        "oracle_answers": None,
        "relation": "was born",

        # Classifier configuration
        "classifier": None,
        "classifier_args": dict(),
        "dimensionality_reduction": None,
        "dimensionality_reduction_dimension": None,
        "feature_selection": None,
        "feature_selection_dimension": None,
        "scaler": True,
        "sparse": False,
        "features": None
    }

    bowreduced = make_feature_list("""
                bag_of_words_in_between
                bag_of_pos_in_between""")
    bowwide = make_feature_list("""
                bag_of_words_in_between
                bag_of_pos_in_between""")
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
    xtrabow = make_feature_list("""
                bag_of_word_bigrams
                bag_of_wordpos
                bag_of_wordpos_bigrams
                bag_of_word_bigrams_in_between
                bag_of_wordpos_in_between
                bag_of_wordpos_bigrams_in_between
                BagOfVerbStems True
                BagOfVerbStems False
                BagOfVerbLemmas True
                BagOfVerbLemmas False
        """)

    """
    patch = {"oracle_answers": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 150, 200]}

    xs = [("sgd", bowfeats, True),
          ("sgd", bowfeats + densefeats, True),
          ("adaboost", bowfeats, False),
          ("svm", densefeats, False),
          ("svm", bowfeats + densefeats, True)]
    """
    patch = {"oracle_answers": list(range(10, 150))}
    xs = [("sgd", bowfeats, True),
          ("sgd", bowreduced, True),
          ("sgd", bowwide, True)]

    for classifier, features, sparse in xs:
        base["classifier"] = classifier
        base["features"] = features
        base["sparse"] = sparse
        for config in apply_dict_combinations(base, patch):
            yield config


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.DEBUG)

    opts = docopt(__doc__)

    configs = list(iter_configs())
    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(",", ": "))
