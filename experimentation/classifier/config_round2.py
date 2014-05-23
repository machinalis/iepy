# -*- coding: utf-8 -*-
u"""
Experimental evaluation round 2.

Usage:
    config_round2.py <testdata.csv> <dbname>

Options:
 -h --help              Show this screen.

The testdata.csv argument is a csv file containing the gold standard to be used
to evaluate the different configurations. The absolute path and the md5 of the
file will be added to the configurations.


Description:
Regarding the statistical classification stage of IEPY, the goal of this
round of experiments is:
    - Obtain configurations for SVM and Adaboost that yield higher
      performance than out-of-the-box.

To do that, configurations will:
    - Explore a variety of configurations for SVM and Adaboost.
"""

import os
import hashlib

from utils import apply_dict_combinations, check_configs
from iepy.utils import make_feature_list


def iter_configs(input_file_path, dbname):
    input_file_path = os.path.abspath(input_file_path)
    hasher = hashlib.md5(open(input_file_path, "rb").read())
    base = {
        # Experiment configuration
        u"config_version": u"1",
        u"data_shuffle_seed": None,
        u"train_percentage": None,
        u"input_file_path": input_file_path,
        u"input_file_md5": hasher.hexdigest(),
        u"database_name": dbname,

        # Classifier configuration
        u"classifier": u"svm",
        u"classifier_args": dict(),
        u"dimensionality_reduction": None,
        u"dimensionality_reduction_dimension": None,
        u"feature_selection": None,
        u"feature_selection_dimension": 1000,
        u"scaler": True,
        u"sparse": False,
        u"features": make_feature_list(u"""
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

    # SVM
    ######
    patch = {u"train_percentage": [0.05 * x for x in range(1, 11)],
             u"data_shuffle_seed": [u"daddycool" + str(i) for i in range(20)],
             u"feature_selection": [None, "kbest"]}
    svm_args_patches = [
        {u"kernel": [u"rbf"], u"C": [1, 10, 100],
         u"gamma": [0.0, 0.001, 0.0001]},
        {u"kernel": [u"poly"], u"C": [1, 10, 100], u"degree": [2, 3, 4],
         u"gamma": [0.0, 0.001, 0.0001]},
        {u"kernel": [u"linear"], u"C": [1, 10, 100]},
    ]

    for argpatch in svm_args_patches:
        for argconfig in apply_dict_combinations({}, argpatch):
            base[u"classifier_args"] = argconfig
            for config in apply_dict_combinations(base, patch):
                yield config

    # Adaboost
    ###########

    base.update({
        u"classifier": u"adaboost",
        u"feature_selection_dimension": None,
        u"scaler": False,
    })

    patch = {u"train_percentage": [0.05 * x for x in range(1, 11)],
             u"data_shuffle_seed": [u"daddycool" + str(i) for i in range(10)]}
    argpatch = {u"n_estimators": [5, 10, 20, 50],
                u"learning_rate": [0.9, 1.0, 1.1],
                u"max_depth": [1, 2, 3]}
    for argconfig in apply_dict_combinations({}, argpatch):
        base[u"classifier_args"] = argconfig
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
    requiered = [{u"classifier": u"svm",
                  u"scaler": True},
                 #{u"classifier": u"adaboost",
                 # u"scaler": False}
                 ]
    # Requiered to be excluded from all configs
    excluded = [{u"feature_selection": u"dtree",
                 u"classifier": u"adaboost"},
                {u"feature_selection": u"kbest",
                 u"classifier": u"adaboost"}]
    configs = list(iter_configs(opts[u"<testdata.csv>"], opts[u"<dbname>"]))
    check_configs(configs, requiered, excluded)

    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
