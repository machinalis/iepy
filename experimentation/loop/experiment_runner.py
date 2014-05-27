"""
Experiment definition for fine tuning the whole IEPY looping
"""
import hashlib
import random
import time

from featureforge.experimentation import runner

from iepy.knowledge import Knowledge
import iepy.db
from iepy.pycompatibility import PY2
from iepy.core import BootstrappedIEPipeline

#
# The class below is one way (an ugly one) to solve the issue of getting the
# data file path into train_and_evaluate_classifier without having it in
# the booked configuration.
# There are other ways to do it, this one I hated less.
#


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
        keep_looping = True
        round_nr = 1
        while keep_looping and round_nr <= self.rounds:
            round_nr += 1
            questions = list(self.questions_available())
            if not questions:
                keep_looping = False

            answered = 0
            for evidence, rank in questions:
                reference_answer = self.gold_standard.get(evidence, None)
                answers_given.append(reference_answer)
                if reference_answer in [1.0, 0.0]:
                    self.add_answer(evidence, reference_answer)
                    answered += 1
                if answered == self.answers_per_round:
                    # enough answering for this round
                    break
            self.force_process()  # blocking
        return answers_given


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
        data = self.get_data(config)
        db_con = iepy.db.connect(self.dbname)
        seed_facts = self.build_seed_facts(data, config)

        result = {
            "seed_facts": seed_facts,
            "dataset_size": len(data),
            "start_time": time.time(),
        }

        # Train
        iepyloop = ReferenceProxyBootstrappedIEPipeline(
            db_connector=db_con, seed_facts=seed_facts, gold_standard=data,
            rounds=config[u'max_number_of_rounds'],
            answers_per_round=config[u'answers_per_round'],
            extractor_config=config[u'classifier_config'],
            prediction_config=config[u'prediction_config'],
            evidence_threshold=config[u'evidence_threshold'],
            fact_threshold=config[u'fact_threshold'],
            sort_questions_by=config[u'questions_sorting']
        )

        answers_given = iepyloop.run_experiment()
        result[u'answers_given'] = answers_given

        # Evaluate
        correct = []
        incorrect = []
        tp, fp, tn, fn = 0.0, 0.0, 0.0, 0.0
        predicted_labels = extractor.predict(test_evidences)
        for i, predicted_label in zip(test, predicted_labels):
            evidence, real_label = data[i]
            if real_label == predicted_label:
                correct.append(i)
                if real_label:
                    tp += 1
                else:
                    tn += 1
            else:
                incorrect.append(i)
                if predicted_label:
                    fp += 1
                else:
                    fn += 1

        # Make stats
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
        result.update({
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "accuracy": (tp + tn) / len(data),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "correctly_predicted": correct,
            "incorrectly_predicted": incorrect,
            "end_time": time.time()
        })
        return result

    def get_data(self, config):
        if self.last_dbname != self.dbname or self.last_path != self.path or \
           self.last_hash != config[u"input_file_md5"]:
            iepy.db.connect(self.dbname)
            self.data = Knowledge.load_from_csv(self.path)
            self.last_dbname = self.dbname
            self.last_path = self.path
            hasher = hashlib.md5(open(self.path, "rb").read())
            self.last_hash = hasher.hexdigest()
            if self.last_hash != config[u"input_file_md5"]:
                raise ValueError("Configured input file and actual input "
                                 "file have different MD5 checksums")
        return self.data

    def build_seed_facts(self, data, config):
        seeds_info = config[u'seed_facts']
        possible_seeds = []
        for ev, s in data.items():
            if s != 1.0 or ev.fact in possible_seeds:
                continue
            possible_seeds.append(ev.fact)
        r = random.Random()
        r.seed(seeds_info[u'shuffle'])
        return r.sample(possible_seeds, seeds_info[u'number_to_use'])

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
                booking_duration=60 * 15,  # 15 minutes
                use_git_info_from_path=path)
