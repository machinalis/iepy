# -*- coding: utf-8 -*-
u"""
Experimental evaluation round 3.

Usage:
    config_round3.py <testdata.csv> <dbname>

Options:
 -h --help              Show this screen.

The testdata.csv argument is a csv file containing the gold standard to be used
to evaluate the different configurations. The absolute path and the md5 of the
file will be added to the configurations.


Description:
Regarding the statistical classification stage of IEPY, the goal of this
round of experiments is:
    - Obtain configurations for SVM that yield high precision across many train
      sizes.

To do that, configurations will:
    - Explore a variety of configurations for SVM:
        - RBF kernel (4*5 = 20 configurations):
            - 4 gamma values: [0.0, 1e-4, 1e-5, 1e-6].
            - 5 class weights: [(10, 1), (1, 0.1), (1, 1), (0.1, 1), (1, 10)].
            - No feature selection.
        - Polynomial kernel  (4*5*4 = 80 configurations):
            - Degree 4.
            - 4 gamma values: [0.0, 1e-4, 1e-5, 1e-6].
            - 5 class weights: [(10, 1), (1, 0.1), (1, 1), (0.1, 1), (1, 10)].
            - KBest feature selection with 4 dimensions: [500, 1000, 2000, 4000].
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
        u"feature_selection_dimension": None,
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

    # RBF
    ######
    patch = {u"train_percentage": [0.07 * x for x in range(1, 11)],
             u"data_shuffle_seed": [u"sussieq" + str(i) for i in range(20)]}
    argpatch = {
        u"kernel": [u"rbf"],
        u"gamma": [0.0, 1e-4, 1e-5, 1e-6],
        u"class_weight": [{True: 10, False: 1},
                          {True: 1, False: 10},
                          {True: 1, False: 1},
                          {True: 1, False: 0.1},
                          {True: 0.1, False: 1}]
    }

    for argconfig in apply_dict_combinations({}, argpatch):
        base[u"classifier_args"] = argconfig
        for config in apply_dict_combinations(base, patch):
            yield config


    # POLY
    #######

    base[u"feature_selection"] = "kbest"
    patch = {u"train_percentage": [0.07 * x for x in range(1, 11)],
             u"data_shuffle_seed": [u"sussieq" + str(i) for i in range(20)],
             u"feature_selection_dimension": [500, 1000, 2000, 4000]}

    argpatch = {
        u"kernel": [u"poly"], u"degree": [4],
        u"gamma": [0.0, 1e-4, 1e-5, 1e-6],
        u"class_weight": [{True: 10, False: 1},
                          {True: 1, False: 10},
                          {True: 1, False: 1},
                          {True: 1, False: 0.1},
                          {True: 0.1, False: 1}]
    }

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
    # Required to be included in some config
    required = [{u"classifier": u"svm",
                  u"scaler": True},
                 #{u"classifier": u"adaboost",
                 # u"scaler": False}
                 ]
    # Required to be excluded from all configs
    excluded = [{u"feature_selection": u"dtree",
                 u"classifier": u"adaboost"},
                {u"feature_selection": u"kbest",
                 u"classifier": u"adaboost"}]
    configs = list(iter_configs(opts[u"<testdata.csv>"], opts[u"<dbname>"]))
    always = "config_version data_shuffle_seed train_percentage".split()
    check_configs(configs, required, excluded, always=always)

    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
