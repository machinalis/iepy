# -*- coding: utf-8 -*-
from itertools import product
import datetime
import logging

from iepy.extraction.relation_extraction_classifier import RelationExtractionClassifier


logger = logging.getLogger('experimentation.utils')


def apply_dict_combinations(base, options):
    base = dict(base)
    group = [list(product([name], vals)) for name, vals in options.items()]
    for combination in product(*group):
        base.update(combination)
        yield dict(base)


def _includes(config, include):
    new = dict(config)
    new.update(include)
    return new == config


def check_configs(configs, includes=None, excludes=None, always=None,
                  estimated_minutes_per_config=1):
    if includes is None:
        includes = []
    if excludes is None:
        excludes = []
    if always is None:
        always = []
    for N, config in enumerate(configs):
        for exclude in excludes:
            if _includes(config, exclude):
                raise ValueError("config includes an excluded dict",
                                 config, exclude)
        for i, include in enumerate(includes):
            if _includes(config, include):
                del includes[i]
        for key in always:
            if key not in config:
                raise ValueError("Mandatory key is missing in dict", key,
                                 config)
        if 'classifier_config' in config:
            # config dict wraps a classifier config. Let's check it inside
            RelationExtractionClassifier(config['classifier_config'])
        else:
            RelationExtractionClassifier(config)
    N += 1
    if includes:
        raise ValueError("No configuration included {}".format(list(includes)))
    logger.info("All ok (ie, not plain wrong).")
    logger.info("Explored {} configs.".format(N))
    t = datetime.timedelta(seconds=N * estimated_minutes_per_config * 60)
    logger.info("At {} minutes per config this would take "
                "aproximately {} (h:mm:ss)".format(estimated_minutes_per_config, t))
