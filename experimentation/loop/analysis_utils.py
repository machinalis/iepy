# -*- coding: utf-8 -*-
"""
Analysis utils: Helper functions for the result analysis ipython notebooks.

Since experiments results have different structure for looping experimentation than
for classifier experimentation, some code is kind-of-repeated in here with the
needed changes.

"""

from collections import defaultdict
import pprint
import copy
import time

from prettytable import PrettyTable
import pygal
from IPython.display import display, HTML

from featureforge.experimentation.stats_manager import StatsManager


def retrieve_and_organize_experiments(dbname, server, experiments_rounds=None):
    def rday(r):
        t = r[u'results'][u'start_time']
        t = time.gmtime(t)
        return (t.tm_year, t.tm_mon, t.tm_mday)

    def rdatasize(r):
        return r[u'results'][u'dataset_size']

    def rkey(r):
        return (r[u'config_version'],
                r[u'git_info'],
                r[u"input_file_md5"],
                tuple(r[u"database_hash"])
                )

    sm = StatsManager(1, dbname, server)
    exp_filter = {sm.experiment_status: sm.STATUS_SOLVED}
    if experiments_rounds is not None:
        if not isinstance(experiments_rounds, list):
            experiments_rounds = [experiments_rounds]
        experiments_rounds = list(map(str, experiments_rounds))
        exp_filter['config_version'] = {'$in': experiments_rounds}
    alldatapoints = list(sm.data.find(exp_filter))
    groupeddata = defaultdict(list)
    for r in alldatapoints:
        del r["booked_at"]
        del r["_id"]
        groupeddata[rkey(r)].append(r)
    alldata = sorted(groupeddata.values(), key=lambda x: rday(x[0]))
    print("\n id date\truns\tdataset size")
    for i, xs in enumerate(alldata):
        date = "/".join("{:02}".format(x) for x in rday(xs[0]))
        print("{: 3} {}\t{}\t{}".format(i, date, len(xs), rdatasize(xs[0])))
    return alldata


def expand_data_points(datapoints):
    """Since each of our experiments implies several rounds of prediction, we expand
    the stats about each round"""
    ## Expand each data point according to each round
    xp_data = []
    for exp in datapoints:
        exp = copy.deepcopy(exp)
        r = exp['results']
        answers = r.pop('answers_given')
        answers_per_round = exp[u'answers_per_round']
        rounds_stuff = r.pop('learning_numbers')
        for round_nr, learning_stats in enumerate(rounds_stuff, 1):
            exp = copy.deepcopy(exp)
            r = exp['results']
            r['answers_given'] = answers[:round_nr*answers_per_round]
            r['learning_stats'] = learning_stats
            r['round'] = round_nr
            xp_data.append(exp)
    print('Expanded datapoints from %s to %s' % (len(datapoints), len(xp_data)))
    return xp_data


def pprint_solution(d):
    delfields = "results classifier_config database_hash data_shuffle_seed config_version input_file_md5 marshalled_key git_info".split()
    delfields.extend("experiment experiment_status".split())
    d = copy.deepcopy(d)
    for name in delfields:
        del d[name]
    pprint.pprint(d)


def get_key(point, key, default=None):
    """Utility for easyly getting values on nested dictionaries or lists
    the provided key is splitted by points, using each subkey in order
    """
    key_path = key.split('.')
    value = point
    for k in key_path:
        if not isinstance(value, dict):
            # we'll use k as index
            value = value[int(k)]
        else:
            value = value.get(k, default)
    return value


def avg_var(values):
    """Computes average and standar var out of a list of values"""
    avg = sum(values) / float(len(values))
    if len(values) == 1:
        var = 0
    else:
        var = sum((y - avg) ** 2 for y in values) / (len(values) - 1)
    return avg, var


def galplot(xs, x_path, y_path, exclude_criteria=None, labeler=None, group_by=None):
    if callable(exclude_criteria):
        xs = exclude_criteria(xs)

    if callable(group_by):
        xxs = group_by(xs)
    else:
        if isinstance(xs, dict):
            xxs = dict(xs.items())
        else:
            xxs = dict([(nr, [x]) for nr, x in enumerate(xs, 1)])

    if callable(x_path):
        x_title = getattr(x_path, 'func_name', 'x')
        get_x = x_path
    else:
        x_title = x_path.split('.')[-1]
        get_x = lambda pt: get_key(pt, x_path)

    if callable(y_path):
        y_title = getattr(y_path, 'func_name', 'y')
        get_y = y_path
    else:
        y_title = y_path.split('.')[-1]
        get_y = lambda pt: get_key(pt, y_path)

    xy_chart = pygal.XY(stroke=True,
                        x_title=x_title,
                        y_title=y_title,
                        disable_xml_declaration=True)

    for group, points in xxs.items():
        if labeler:
            lbl = str(labeler(points[0]))
        else:
            lbl = '%s' % group
        xy_chart.add(lbl, [(get_x(pt), get_y(pt)) for pt in points])

    display(HTML("""
    <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/svg.jquery.js"></script>
    <script type="text/javascript" src="http://kozea.github.com/pygal.js/javascripts/pygal-tooltips.js"></script>
    """))
    display(HTML(xy_chart.render()))


def versus(dataset, key_path, use_len=False):
    """Given a group of experiments, split them in groups based on key_path, and
    prints a table comparing them"""
    _answers_path = 'results.answers_given'
    groups = defaultdict(list)
    for pt in dataset:
        grp_id = get_key(pt, key_path)
        if use_len:
            grp_id = len(grp_id)
        if isinstance(grp_id, list):
            grp_id = str(grp_id)  # unhashable otherwise
        groups[grp_id].append(pt)

    table = PrettyTable(["Options", u"Vts(↑)", "ML", u"Vts/ans(↑)",
                         "Ans/Yes(↓)", "F1(↑↓)", "Prec(↑↓)", "Recall(↑↓)"])
    table.align["Options"] = "l"

    for grp_id, gr in sorted(groups.items()):
        votes = len(gr)
        answers = reduce(lambda x, y: x+y, [get_key(pt, _answers_path) for pt in gr])
        machine_learnt = [get_key(pt, 'results.learning_stats.machine_learnt') for pt in gr]
        machine_acc = [get_key(pt, 'results.learning_stats.machine_accuracy') for pt in gr]

        yes_nr = float(answers.count(1.0))

        row = [grp_id, votes,
               # ML
               '%.2f (%.2f) - %.2f%% (%.2f)' % (avg_var(machine_learnt) + avg_var(machine_acc)),

               '%.5f' % (float(votes) / len(answers)),
               '%.2f' % (len(answers) / yes_nr)]
        kn = "results.learning_stats.knownledge."
        for path in [kn+"f1", kn+"precision", kn+"recall"]:
            values = [100. * get_key(pt, path) for pt in gr]
            avg, var = avg_var(values)
            row.append('%.1f %.1f' % (avg, var))

        table.add_row(row)

    print 'Versus info for %s' % key_path
    print table

ml_path = 'results.learning_stats.machine_learnt'
ml_pre = 'results.learning_stats.machine_accuracy'
kn_pre = 'results.learning_stats.knownledge.precision'
kn_rec = 'results.learning_stats.knownledge.recall'
kn_f1 = 'results.learning_stats.knownledge.f1'


def descends_more_than_expected_per_round(experiments, key_path,
                                          ommit_first_N, delta_accepted):
    prev = experiments[ommit_first_N]
    for el in experiments[ommit_first_N+1:]:
        if get_key(el, key_path) + delta_accepted < get_key(prev, key_path):
            return True
        prev = el
    return False


def results_cmp(el):
    """when we decide that experiments seems to be similar"""
    # returns the pieces of results to use for a comparison
    return map(lambda x: get_key(el, x), [ml_path, ml_pre, kn_pre, kn_rec,
                                          'results.answers_given'])


def group_by_hash_and_filter(xs, final_P=None, final_R=None, min_MA=None, min_ML=None,
                             max_ML=None, F1_degr=None, P_degr=None, F1_gain=None):
    xxs = defaultdict(list)
    for x in xs:
        xxs[x[u'marshalled_key']].append(x)
    print ('Created %s groups from %s initial elements' % (len(xxs), len(xs)))
    # Will now remove groups with very bad general numbers
    for group, elems in list(xxs.items()):
        # If final prec and recall are not both higher than F_P & F_R, go home
        if final_P is not None and get_key(elems[-1], kn_pre) < final_P:
            del xxs[group]
            continue
        if final_R is not None and get_key(elems[-1], kn_rec) < final_R:
            del xxs[group]
            continue
        # If machine accuracy is never higher than min_MA, go home
        if min_MA is not None and all(get_key(el, ml_pre) < min_MA for el in elems):
            del xxs[group]
            continue
        # If machine learnt is never higher than min_ML, go home
        if min_ML is not None and all(get_key(el, ml_path) < min_ML for el in elems):
            del xxs[group]
            continue
        # If N elems have proposed more than MML, go home
        if max_ML is not None:
            N, MML = max_ML
            if len([el for el in elems if get_key(el, ml_path) > MML]) > N:
                del xxs[group]
                continue
        # On each round, (after X rounds, for stability) F1 shall not degrade more than
        # F1_degr, otherwise go home
        if F1_degr is not None:
            delta, ommit = F1_degr
            if descends_more_than_expected_per_round(elems, kn_f1, ommit, delta):
                del xxs[group]
                continue
        # And same for global P
        if P_degr is not None:
            delta, ommit = P_degr
            if descends_more_than_expected_per_round(elems, kn_pre, ommit, delta):
                del xxs[group]
                continue

        # If IEPY F1 did not grow up F1_gain, go home
        if F1_gain is not None and get_key(elems[-1], kn_f1) < F1_gain + get_key(elems[0], kn_f1):
            del xxs[group]
            continue

    print ('Left %s groups after filters' % len(xxs))
    new_xxs = {}
    for group, elems in xxs.items():
        elems = sorted(elems, key=lambda e: e['results']['round'])
        for n_g, n_elems in list(new_xxs.items()):
            if [results_cmp(e) for e in elems] == [results_cmp(e) for e in n_elems]:
                #print 'Hiding %s behind %s'  % (group, n_g)
                break  # already considered
        else:
            new_xxs[group] = elems

    print ('And after regrouping according similarity, left %s' % len(new_xxs))
    return new_xxs
