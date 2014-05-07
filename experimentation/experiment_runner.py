import hashlib
import random
import time

from featureforge.experimentation import runner

from iepy.fact_extractor import FactExtractorFactory
from iepy.knowledge import Knowledge
import iepy.db


#
# The class below is one way (an ugly one) to solve the issue of getting the
# data file path into train_and_evaluate_classifier without having it in
# the booked configuration.
# There are other ways to do it, this one I hated less.
#

class Runner(object):
    def __init__(self):
        self.last_dbname = None
        self.last_path = None
        self.last_hash = None

    def train_and_evaluate_classifier(self, config):
        assert self.config == config
        assert "input_file_path" not in config
        assert "database_name" not in config

        # Prepare data
        data = self.get_data(config)
        train, test = self.get_train_test_indexes(config, len(data))
        train = dict(data[i] for i in train)
        test_evidences = (data[i][0] for i in test)

        result = {
            "train_size": len(train),
            "test_size": len(test),
            "dataset_size": len(data),
            "start_time": time.time(),
        }

        # Train
        extractor = FactExtractorFactory(config, train)

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
                if real_label:
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
            data = sorted(Knowledge.load_from_csv(self.path).items())
            self.data = data
            self.last_dbname = self.dbname
            self.last_path = self.path
            hasher = hashlib.md5(open(self.path, "rb").read())
            self.last_hash = hasher.hexdigest()
            if self.last_hash != config[u"input_file_md5"]:
                raise ValueError("Configured input file and actual input "
                                 "file have different MD5 checksums")
        return self.data

    def get_train_test_indexes(self, config, N):
        r = random.Random()
        r.seed(config[u"data_shuffle_seed"])
        indexes = list(range(N))
        r.shuffle(indexes)
        n = int(config[u"train_percentage"] * N)
        return indexes[:n], indexes[n:]

    def extender(self, config):
        config["features"] = set(config["features"])
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


if __name__ == '__main__':
    import os.path
    import logging

    logging.basicConfig(level=logging.DEBUG)

    path = os.path.abspath(os.path.dirname(__file__))

    r = Runner()
    runner.main(r.train_and_evaluate_classifier, r.extender,
                booking_duration=60 * 3,  # 3 minutes
                use_git_info_from_path=path)
