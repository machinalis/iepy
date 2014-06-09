# -*- coding: utf-8 -*-
u"""
Bootstrap Experimental evaluation round 6.

Usage:
    config_round6.py <testdata.csv> <dbname>

Options:
 -h --help              Show this screen.

The testdata.csv argument is a csv file containing the gold standard to be used
to evaluate the different configurations. The absolute path and the md5 of the
file will be added to the configurations.

"""
import os
import hashlib
from itertools import product
from copy import deepcopy

from iepy.utils import make_feature_list

from utils import apply_dict_combinations, check_configs

features = make_feature_list(u"""
                bag_of_words_in_between
                bag_of_pos_in_between
                bag_of_wordpos_in_between
                entity_order
                entity_distance
                other_entities_in_between
                verbs_count_in_between""")


# Proposing as classifiers the champions of the
# experimentation/classifier/config_round5.py
# Note: they will suffer small modifications (on feature_selection_dimension)
candidate_classifiers = [
    {
        u'classifier': u'svm',
        u'classifier_args': {
            u'class_weight': {u'false': 1, u'true': 1},
            u'gamma': 0.0,
            u'kernel': u'rbf'
        },
        u'dimensionality_reduction': None,
        u'dimensionality_reduction_dimension': None,
        u'feature_selection': u'frequency_filter',
        u'feature_selection_dimension': 5,  # altered to 10
        u'scaler': True,
        u'sparse': True,
        u'features': features[:]
    },
    {
        u'classifier': u'svm',
        u'classifier_args': {
            u'class_weight': {u'false': 10, u'true': 1},
            u'gamma': 0.0,
            u'kernel': u'rbf'
        },
        u'dimensionality_reduction': None,
        u'dimensionality_reduction_dimension': None,
        u'feature_selection': u'frequency_filter',
        u'feature_selection_dimension': 5,  # altered to 10
        u'scaler': True,
        u'sparse': True,
        u'features': features[:]
    }
]

loop_champions_round_4 = [
    {
        "was_on_round_4": "d135",
        "answers_per_round": 3,
        "classifier_config": {},
        "data_shuffle_seed": "a-ha",
        "drop_guesses_each_round": True,
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
        "classifier_config": {},
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
        "classifier_config": {},
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
        "classifier_config": {},
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


def iter_configs(input_file_path, dbname):
    input_file_path = os.path.abspath(input_file_path)
    hasher = hashlib.md5(open(input_file_path, 'rb').read())
    base = {
        # Experiment configuration
        u'config_version': u'6',
        u'input_file_path': input_file_path,
        u'input_file_md5': hasher.hexdigest(),
        u'database_name': dbname
    }

    prediction_patch = {
        u'method': [u'predict', u'predict_proba', 'decision_function'],
    }
    seed_patch = {
        u'shuffle': [u"%i lemon and half lemon" % i for i in range(3)]
    }

    for champ, classifier in product(loop_champions_round_4, candidate_classifiers):
        champ = deepcopy(champ)
        champ.update(base)
        champ['classifier_config'] = deepcopy(classifier)

        prediction_options_range = list(
            apply_dict_combinations(champ['prediction_config'], prediction_patch)
        )
        seed_options_range = list(
            apply_dict_combinations(champ[u'seed_facts'], seed_patch)
        )
        patch = {
            u'prediction_config': prediction_options_range,
            u'questions_sorting': [u'score', u'certainty'],
            u'seed_facts': seed_options_range
        }
        for config in apply_dict_combinations(champ, patch):
            yield config
            config = deepcopy(config)
            config['classifier_config']['feature_selection_dimension'] = 10
            if config['prediction_config']['method'] == u'predict_proba':
                config['classifier_config']['classifier_args'][u'probability'] = True
            yield config


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.INFO)

    opts = docopt(__doc__)
    configs = list(iter_configs(opts[u'<testdata.csv>'], opts[u'<dbname>']))
    check_configs(configs, estimated_minutes_per_config=8)
    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
