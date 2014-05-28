"""
Experiment definition for fine tuning the whole IEPY looping
"""
from copy import copy
import hashlib
from operator import itemgetter
import random
import time

from featureforge.experimentation import runner
from sklearn.metrics import log_loss

from iepy.knowledge import Knowledge
import iepy.db
from iepy.pycompatibility import PY2
from iepy.core import BootstrappedIEPipeline

from average_precision import apk


def precision_recall_f1(true_pos, false_pos, false_neg):
    # Make stats
    tp, fp, fn = map(float, [true_pos, false_pos, false_neg])
    try:
        precision = tp / (tp + fp)
    except ZeroDivisionError:
        precision = 1.0
    try:
        recall = tp / (tp + fn)
    except ZeroDivisionError:
        recall = 1.0
    try:
        f1 = 2 * (precision * recall) / (precision + recall)
    except ZeroDivisionError:
        f1 = 0.0
    return precision, recall, f1


class ReferenceProxyBootstrappedIEPipeline(BootstrappedIEPipeline):
    """Wraps the classic pipeline, providing:
        - automatic question answering, replacing Human In The Loop (uses
          the reference corpus)
    """

    def __init__(self, *args, **kwargs):
        self.rounds = kwargs.pop('rounds')
        self.answers_per_round = kwargs.pop('answers_per_round')
        super(ReferenceProxyBootstrappedIEPipeline, self).__init__(*args, **kwargs)

    def run_experiment(self):
        self.start()  # blocking
        answers_given = []
        progression = []
        keep_looping = True
        round_nr = 0
        while keep_looping and round_nr < self.rounds:
            round_nr += 1
            questions = list(self.questions_available())
            if not questions:
                keep_looping = False

            answered = 0
            for evidence, rank in questions:
                reference_answer = self.gold_standard.get(evidence, None)
                answers_given.append((evidence, reference_answer))
                if reference_answer in [1.0, 0.0]:
                    self.add_answer(evidence, reference_answer)
                    answered += 1
                if answered == self.answers_per_round:
                    # enough answering for this round
                    break
            self.force_process()  # blocking
            progression.append((copy(self.knowledge),
                                copy(self.evidence)))
        return answers_given, progression


class Runner(object):
    def __init__(self):
        self.last_dbname = None
        self.last_path = None
        self.last_hash = None

    def run_iepy(self, config):
        assert self.config == config
        assert "input_file_path" not in config
        assert "database_name" not in config

        config = _fix_config(config)

        # Prepare data
        self.load_data(config)
        reference = self.data
        all_facts = self.build_facts_list(reference)
        db_con = iepy.db.connect(self.dbname)
        seed_facts = self.pick_seeds_facts(all_facts, config)

        result = {
            "seed_facts": [all_facts.index(seed) for seed in seed_facts],
            "dataset_size": len(reference),
            "start_time": time.time(),
        }

        # Train
        iepyloop = ReferenceProxyBootstrappedIEPipeline(
            db_connector=db_con, seed_facts=seed_facts, gold_standard=reference,
            rounds=config[u'max_number_of_rounds'],
            answers_per_round=config[u'answers_per_round'],
            extractor_config=config[u'classifier_config'],
            prediction_config=config[u'prediction_config'],
            evidence_threshold=config[u'evidence_threshold'],
            fact_threshold=config[u'fact_threshold'],
            sort_questions_by=config[u'questions_sorting']
        )

        answers_given, progression = iepyloop.run_experiment()
        result[u'answers_given'] = [a for q, a in answers_given]
        result[u'prediction_numbers'] = prediction_numbers = []
        result[u'learning_numbers'] = learning_numbers = []
        answers_per_round = config[u'answers_per_round']
        for round_nr, (learnt, prediction) in enumerate(progression, 1):
            prediction_numbers.append(self.prediction_eval(prediction, reference))
            answers_so_far = answers_given[:round_nr*answers_per_round]
            learning_numbers.append(
                self.learning_eval(learnt, seed_facts, all_facts, answers_so_far, reference)
            )
        return result

    def learning_eval(self, learnt, seed_facts, all_facts, answers_given, reference):
        learnt_facts = set([ev.fact for ev in learnt])
        all_facts_set = set(all_facts)  # made set to have Set methods
        # Strange Precision & recall measure about "facts"
        facts_precision, facts_recall, facts_f1 = precision_recall_f1(
            len(all_facts_set.intersection(learnt_facts)),
            len(learnt_facts.difference(all_facts)),
            len(all_facts_set.difference(learnt_facts))
        )
        human_learnt = [ev for ev, answers in answers_given if answers]
        human_learnt_facts = set([ev.fact for ev in human_learnt])
        human_learnt_facts = human_learnt_facts.union(seed_facts)
        assert len(learnt_facts) >= len(human_learnt_facts)
        assert len(learnt) >= len(human_learnt)

        return {
            # some stats about facts only
            u'facts_precision': facts_precision,
            u'facts_recall': facts_recall,
            u'facts_f1': facts_f1,
            u'facts_size': len(learnt_facts),

            # some stats about things learnt only thanks to human
            u'human_learnt_facts_size': len(human_learnt_facts),
            u'human_learnt_size': len(human_learnt),
            u'knownledge_size': len(learnt),

            # and now the tipical info re the knowledge gained
            u'knownledge': self.knowledge_stats(learnt, reference),
            u'end_time': time.time()
        }

    def knowledge_stats(self, knowledge, reference):
        # things on the knowledge object that are not in the reference will
        # be simply logged, but not used for computations
        unknown = list(set(knowledge.keys()).difference(reference.keys()))
        correct = []
        incorrect = []
        tp, fp, tn, fn = 0.0, 0.0, 0.0, 0.0
        for ev_idx, evidence in enumerate(sorted(reference.keys())):
            # If it's part of knowledge, then is taken as valid
            if evidence in knowledge:
                learnt_label = 1.0
            else:
                learnt_label = 0.0
            real_label = reference[evidence]
            if real_label == learnt_label:
                correct.append(ev_idx)
                if real_label == 1.0:
                    tp += 1
                else:
                    tn += 1
            else:
                incorrect.append(ev_idx)
                if learnt_label:
                    fp += 1
                else:
                    fn += 1

        # Make stats
        precision, recall, f1 = precision_recall_f1(tp, fp, fn)
        return {
            u'true_positives': tp,
            u'false_positives': fp,
            u'true_negatives': tn,
            u'false_negatives': fn,
            u'accuracy': (tp + tn) / len(reference),
            u'precision': precision,
            u'recall': recall,
            u'f1': f1,
            u'correctly_learnt': correct,
            u'incorrectly_learnt': incorrect,
            u'unknown': [str(u) for u in unknown]
        }

    def prediction_eval(self, prediction, reference):
        # things on the prediction object that are not in the reference will
        # be simply ignored
        keys = sorted(reference.keys())
        real_labels = []
        predicted_labels = []
        for key in keys:
            real_labels.append(reference[key])
            prob_1 = prediction[key]
            predicted_labels.append(
                [1-prob_1, prob_1]
            )

        actual_ev = [ev for ev, s in reference.items() if s == 1.0]
        predicted_ev, _ = zip(
            *sorted(prediction.items(), key=itemgetter(1))
        )
        return {
            u'log_loss': log_loss(real_labels, predicted_labels),
            u'avg_len_actual': apk(actual_ev, predicted_ev, k=len(actual_ev)),
            u'avg_len_predic': apk(actual_ev, predicted_ev, k=len(predicted_ev))
        }

    def load_data(self, config):
        if self.last_dbname != self.dbname or self.last_path != self.path or \
           self.last_hash != config[u"input_file_md5"]:
            iepy.db.connect(self.dbname)
            data = Knowledge.load_from_csv(self.path)
            self.last_dbname = self.dbname
            self.last_path = self.path
            hasher = hashlib.md5(open(self.path, "rb").read())
            self.last_hash = hasher.hexdigest()
            if self.last_hash != config[u"input_file_md5"]:
                raise ValueError("Configured input file and actual input "
                                 "file have different MD5 checksums")
            self.data = data

    def build_facts_list(self, reference):
        facts = []
        for ev, s in reference.items():
            if s != 1.0 or ev.fact in facts:
                continue
            facts.append(ev.fact)
        return facts

    def pick_seeds_facts(self, facts_list, config):
        seeds_info = config[u'seed_facts']
        r = random.Random()
        r.seed(seeds_info[u'shuffle'])
        return r.sample(facts_list, seeds_info[u'number_to_use'])

    def extender(self, config):
        config[u'classifier_config']["features"] = set(config[u'classifier_config']["features"])
        self.path = config["input_file_path"]
        self.dbname = config["database_name"]
        del config["input_file_path"]
        del config["database_name"]
        self.config = config

        # Add a database id/hash
        iepy.db.connect(self.dbname)
        dbhash = (iepy.db.TextSegment.objects.count(),
                  iepy.db.IEDocument.objects.count(),
                  iepy.db.Entity.objects.count())
        config["database_hash"] = dbhash
        return config


def _fix_config(config):
    """
    In python 2 is necesary to change config keys and values to be str and not
    unicode because some parts of scikit-learn will complain.
    """
    if PY2:
        for d in [config]:
            for key, value in list(d.items()):
                del d[key]
                key = str(key)
                if isinstance(value, unicode):
                    value = str(value)
                elif isinstance(value, dict):
                    value = _fix_config(value)
                d[key] = value
    return config


if __name__ == '__main__':
    import os.path
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    path = os.path.abspath(os.path.dirname(__file__))

    r = Runner()
    runner.main(r.run_iepy, r.extender,
                booking_duration=60 * 2,  # 2 minutes
                use_git_info_from_path=path)
