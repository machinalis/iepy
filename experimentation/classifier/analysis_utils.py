# -*- coding: utf-8 -*-
"""
Analysis utils: Helper functions for the result analysis ipython notebooks.

"""

from collections import defaultdict
import pprint
import copy
import json
import time
import pylab
import numpy

from featureforge.experimentation.stats_manager import StatsManager
from featureforge.experimentation.utils import DictNormalizer


def myplot(grouping, xkey, ykey, color="Paired", dot="o"):
    pylab.figure(figsize=(13, 13))
    pylab.xlabel(xkey)
    pylab.ylabel(ykey)
    colors = pylab.get_cmap(color)(numpy.linspace(0, 1, len(grouping)))
    for i, (name, xs) in enumerate(sorted(grouping.items())):
        name = name[:100]
        X = [x["results"][xkey] for x in xs]
        Y = [x["results"][ykey] for x in xs]
        X, Y = zip(*sorted(zip(X, Y)))
        pylab.plot(X, Y, dot, color=colors[i], alpha=.99, label=name)
    pylab.legend(loc=2)
    pylab.show()


def pprint_solution(d, delfields=None):
    if not delfields:
        delfields = []
    else:
        delfields = delfields.split()
    delfields.extend("results features database_hash data_shuffle_seed config_version input_file_md5 marshalled_key git_info".split())
    delfields.extend("_id booked_at experiment_status train_percentage".split())
    d = copy.deepcopy(d)
    for name in delfields:
        if name in d:
            del d[name]
    pprint.pprint(d)


def group_by_strategy(xs):
    groups = defaultdict(list)
    normalizer = DictNormalizer()
    delnames = "results marshalled_key data_shuffle_seed train_percentage".split()
    for point in xs:
        d = copy.deepcopy(point)
        for name in delnames:
            del d[name]
        # "booked_at" and "_id" unhashable by the normalizer:
        if "booked_at" in d:
            del d["booked_at"]
        if "_id" in d:
            del d["_id"]
        d = normalizer(d)
        key = json.dumps(d, sort_keys=True)
        groups[key].append(point)
    return dict(groups)

def average_stats(xs):
    groups = defaultdict(list)
    normalizer = DictNormalizer()
    for point in xs:
        d = copy.deepcopy(point)
        del d["results"]
        del d["marshalled_key"]
        del d["data_shuffle_seed"]
        # "booked_at" and "_id" unhashable by the normalizer:
        if "booked_at" in d:
            del d["booked_at"]
        if "_id" in d:
            del d["_id"]
        d = normalizer(d)
        key = json.dumps(d, sort_keys=True)
        groups[key].append(point)
    xs = []
    for ys in groups.values():
        if len(ys) < 10:
            continue
        x = copy.deepcopy(ys[0])
        for name in ["f1", "precision", "recall", "accuracy", "true_positives"]:
            values = [y["results"][name] for y in ys]
            avg = sum(values) / len(values)
            var = sum((y - avg) ** 2 for y in values) / (len(values) - 1)
            del x["results"][name]
            x["results"][name + "_avg"] = avg
            x["results"][name + "_var"] = var
        xs.append(x)
    return xs


def rday(r):
    t = r[u'results'][u'start_time']
    t = time.gmtime(t)
    return (t.tm_year, t.tm_mon, t.tm_mday)

def rdatasize(r):
    return r[u'results'][u'train_size'] + r[u'results'][u'test_size']


def rkey(r):
    return (r[u'config_version'],
            r[u'git_info'],
            r[u"input_file_md5"],
            tuple(r[u"database_hash"]))
#            rday(r))


def pprint_strategy_result(l):
    """Print the results for a specific strategy, ordered by train_percentage.
    """
    print '%\ttp\tP\tR\tF1'
    for p in sorted(l, key=lambda p: p[u'train_percentage']):
        print '{}\t{:.2f}\t{:.2f}\t{:.2f}\t{:.2f}'.format(p[u'train_percentage'], p[u'results'][u'true_positives_avg'], p[u'results'][u'precision_avg'], p[u'results'][u'recall_avg'], p[u'results'][u'f1_avg'])
