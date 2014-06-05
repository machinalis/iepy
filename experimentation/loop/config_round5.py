# -*- coding: utf-8 -*-
u"""
Bootstrap Experimental evaluation round 5.

Usage:
    config_round5.py <testdata.csv> <dbname>

Options:
 -h --help              Show this screen.

The testdata.csv argument is a csv file containing the gold standard to be used
to evaluate the different configurations. The absolute path and the md5 of the
file will be added to the configurations.

"""
import os
import hashlib
from copy import deepcopy

from utils import check_configs

features = [
    "BagOfVerbLemmas False",
    "BagOfVerbLemmas True",
    "BagOfVerbStems False",
    "BagOfVerbStems True",
    "bag_of_pos_in_between",
    "bag_of_word_bigrams_in_between",
    "bag_of_wordpos_bigrams_in_between",
    "bag_of_wordpos_in_between",
    "bag_of_words_in_between",
    "entity_distance",
    "entity_order",
    "in_same_sentence",
    "number_of_tokens",
    "other_entities_in_between",
    "symbols_in_between",
    "total_number_of_entities",
    "verbs_count",
    "verbs_count_in_between"
]


# Proposing as configs the champions of the
# experimentation/loop/config_round4.py
champions_round_4 = [
    {
        "was_on_round_4": "d135",
        "answers_per_round": 3,
        "classifier_config": {
            "classifier": "svm",
            "classifier_args": {
                "gamma": 0.0001,
                "probability": True
            },
            "dimensionality_reduction": None,
            "dimensionality_reduction_dimension": None,
            "feature_selection": None,
            "feature_selection_dimension": None,
            "features": features[:],
            "scaler": True,
            "sparse": False
        },
        "data_shuffle_seed": "a-ha",
        "drop_guesses_each_round": False,
        "evidence_threshold": 0.85,
        "experiment": "bootstrap",
        "fact_threshold": 0.85,
        "max_number_of_rounds": 45,
        "prediction_config": {
            "method": "predict_proba",
            "scale_to_range": [
                0.1,
                0.9
            ]
        },
        "questions_sorting": "score",
        "seed_facts": {
            "number_to_use": 5,
            "shuffle": ""
        }
    },
    {
        "was_on_round_4": "15f6",
        "answers_per_round": 5,
        "classifier_config": {
            "classifier": "svm",
            "classifier_args": {
                "gamma": 0.0001,
                "probability": False
            },
            "dimensionality_reduction": None,
            "dimensionality_reduction_dimension": None,
            "feature_selection": None,
            "feature_selection_dimension": None,
            "features": features[:],
            "scaler": True,
            "sparse": False
        },
        "data_shuffle_seed": "a-ha",
        "drop_guesses_each_round": True,
        "evidence_threshold": 0.85,
        "experiment": "bootstrap",
        "fact_threshold": 0.85,
        "max_number_of_rounds": 27,
        "prediction_config": {
            "method": "decision_function",
            "scale_to_range": [
                0.1,
                0.9
            ]
        },
        "questions_sorting": "certainty",
        "seed_facts": {
            "number_to_use": 5,
            "shuffle": ""
        }
    },
    {
        "was_on_round_4": "50b9",
        "answers_per_round": 5,
        "classifier_config": {
            "classifier": "svm",
            "classifier_args": {
                "gamma": 0.0001,
                "probability": False
            },
            "dimensionality_reduction": None,
            "dimensionality_reduction_dimension": None,
            "feature_selection": None,
            "feature_selection_dimension": None,
            "features": features[:],
            "scaler": True,
            "sparse": False
        },
        "data_shuffle_seed": "a-ha",
        "drop_guesses_each_round": True,
        "evidence_threshold": 0.85,
        "experiment": "bootstrap",
        "fact_threshold": 0.8,
        "max_number_of_rounds": 27,
        "prediction_config": {
            "method": "decision_function",
            "scale_to_range": [
                0.1,
                0.9
            ]
        },
        "questions_sorting": "certainty",
        "seed_facts": {
            "number_to_use": 5,
            "shuffle": ""
        }
    },
    {
        "was_on_round_4": "bab7",
        "answers_per_round": 5,
        "classifier_config": {
            "classifier": "svm",
            "classifier_args": {
                "class_weight": "auto",
                "degree": 4,
                "gamma": 0.0,
                "kernel": "poly"
            },
            "dimensionality_reduction": None,
            "dimensionality_reduction_dimension": None,
            "feature_selection": "kbest",
            "feature_selection_dimension": 100,
            "features": features[:],
            "scaler": True,
            "sparse": True
        },
        "data_shuffle_seed": "a-ha",
        "drop_guesses_each_round": True,
        "evidence_threshold": 0.95,
        "experiment": "bootstrap",
        "fact_threshold": 0.9,
        "max_number_of_rounds": 27,
        "prediction_config": {
            "method": "predict",
            "scale_to_range": None
        },
        "questions_sorting": "certainty",
        "seed_facts": {
            "number_to_use": 5,
            "shuffle": ""
        }
    }
]


candidate_classifiers = [
    {
        u'classifier': u'svm',
        u'classifier_args': {'gamma': 0.0001},
        u'dimensionality_reduction': None,
        u'dimensionality_reduction_dimension': None,
        u'feature_selection': None,
        u'feature_selection_dimension': None,
        u'features': features,
        u'scaler': True,
        u'sparse': False},
    {
        u'classifier': u'svm',
        u'classifier_args': {
            u'class_weight': 'auto',
            u'gamma': 0.0001,
            u'kernel': u'rbf'},
        u'dimensionality_reduction': None,
        u'dimensionality_reduction_dimension': None,
        u'features': features,
        u'feature_selection': None,
        u'feature_selection_dimension': None,
        u'scaler': True,
        u'sparse': True,
    },
    {
        u'classifier': u'svm',
        u'classifier_args': {
            u'class_weight': 'auto',
            u'degree': 4,
            u'gamma': 0.0,
            u'kernel': u'poly'},
        u'dimensionality_reduction': None,
        u'dimensionality_reduction_dimension': None,
        u'features': features,
        u'feature_selection': u'kbest',
        u'feature_selection_dimension': 100,
        u'scaler': True,
        u'sparse': True,
    }
]


def iter_configs(input_file_path, dbname):
    input_file_path = os.path.abspath(input_file_path)
    hasher = hashlib.md5(open(input_file_path, 'rb').read())
    base = {
        # Experiment configuration
        u'config_version': u'5',
        u'data_shuffle_seed': "a-ha",
        u'input_file_path': input_file_path,
        u'input_file_md5': hasher.hexdigest(),
        u'database_name': dbname
    }
    seed_shuffles = [u"%i lemon and half lemon" % i for i in range(2)]

    for champ in champions_round_4:
        champ.update(base)
        for shuffle in seed_shuffles:
            champ['seed_facts']['shuffle'] = shuffle
            yield deepcopy(champ)


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.INFO)

    opts = docopt(__doc__)
    configs = list(iter_configs(opts[u'<testdata.csv>'], opts[u'<dbname>']))
    check_configs(configs, estimated_minutes_per_config=18)
    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
