# -*- coding: utf-8 -*-
from itertools import product
import os
import os.path
import datetime
import logging

from iepy.fact_extractor import FactExtractor


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


def check_configs(configs, includes=None, excludes=None, always=None):
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
        FactExtractor(config)
    N += 1
    if includes:
        raise ValueError("No configuration included {}".format(list(includes)))
    logger.info("All ok (ie, not plain wrong).")
    logger.info("Explored {} configs.".format(N))
    t = datetime.timedelta(seconds=N * 1 * 10)
    logger.info("At 1 minutes per config this would take "
                "aproximately {} (h:mm:ss)".format(t))
