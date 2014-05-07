# -*- coding: utf-8 -*-
u"""
Experimental evaluation round 1.

Usage:
    config_round1.py <testdata.csv>

Options:
 -h --help              Show this screen.

The testdata.csv argument is a csv file containing the gold standard to be used
to evaluate the different configurations. The absolute path and the md5 of the
file will be added to the configurations.


Description:
Regarding the statistical classification stage of IEPY, the goal of this
round of experiments is:
    - Have a ball park estimate of how good we can classify evidences without
      much effort.
    - Have an idea of which classifiers are worth exploring more than others.
    - Have an idea of how performance changes

To do that, configurations will:
    - Explore a variety of configurations close to the out-of-the-box defaults.
"""
import os
import hashlib

from utils import apply_dict_combinations, check_configs
from iepy.utils import make_feature_list


def iter_configs(input_file_path):
    input_file_path = os.path.abspath(input_file_path)
    hasher = hashlib.md5(open(input_file_path, "rb").read())
    base = {
        # Experiment configuration
        "config_version": "1",
        "data_shuffle_seed": None,
        "train_percentage": None,
        "input_file_path": input_file_path,
        "input_file_md5": hasher.hexdigest(),

        # Classifier configuration
        "classifier": "svm",
        "classifier_args": dict(),
        "dimensionality_reduction": None,
        "dimensionality_reduction_dimension": None,
        "feature_selection": None,
        "feature_selection_dimension": None,
        "scaler": True,
        "sparse": False,
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
        """)
    }
    patch = {"train_percentage": [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
             "data_shuffle_seed": ["domino" + str(i) for i in range(10)]}

    xs = [("sgd", {}),
          ("naivebayes", {}),
          ("naivebayes_m", {}),
          ("dtree", {"max_depth":4, "min_samples_leaf":5}),
          ("logit", {}),
          ("svm", {}),
          ("adaboost", {})]
    for classifier, args in xs:
        base["classifier"] = classifier
        base["classifier_args"] = args
        for config in apply_dict_combinations(base, patch):
            yield config


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.DEBUG)

    opts = docopt(__doc__)

    # First check that configurations look ok.
    # Requiered to be included in some config
    requiered = [{"classifier": "logit",
                  "feature_selection": None,
                  "scaler": True}]
    # Requiered to be excluded from all configs
    excluded = [{"feature_selection": "dtree",
                 "classifier": "dtree"
                },
                {"feature_selection": "kbest",
                 "classifier": "dtree"
                },
               ]
    configs = list(iter_configs(opts["<testdata.csv>"]))
    check_configs(configs, requiered, excluded)

    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(',', ': '))
