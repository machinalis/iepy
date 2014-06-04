# -*- coding: utf-8 -*-
u"""
Experimental evaluation round 4.

Usage:
    config_round4.py <testdata.csv> <dbname>

Options:
 -h --help              Show this screen.

The testdata.csv argument is a csv file containing the gold standard to be used
to evaluate the different configurations. The absolute path and the md5 of the
file will be added to the configurations.


Description:
Regarding the statistical classification stage of IEPY, the goal of this
round of experiments is:
    - Obtain good configurations for SVM that can be efficiently used with big
    datasets.

To do that, configurations will:
    - Repeat the experiments done in round 3 but with sparse=True to support
    potentially big datasets.
"""

import os
import hashlib

from utils import apply_dict_combinations, check_configs
from iepy.utils import make_feature_list
from config_round3 import iter_configs as round3_iter_configs


def iter_configs(input_file_path, dbname):
    for config in round3_iter_configs(input_file_path, dbname):
        config[u'sparse'] = True
        yield config


if __name__ == '__main__':
    import json
    import sys
    import logging

    from docopt import docopt

    logging.basicConfig(level=logging.DEBUG)

    opts = docopt(__doc__)

    # First check that configurations look ok.
    required = []
    # Required to be excluded from all configs
    excluded = [{u'sparse': False}]
    configs = list(iter_configs(opts[u"<testdata.csv>"], opts[u"<dbname>"]))
    always = "config_version data_shuffle_seed train_percentage".split()
    check_configs(configs, required, excluded, always=always)

    json.dump(configs, sys.stdout, sort_keys=True, indent=4,
              separators=(u',', u': '))
