"""
Experiment runner for FactExtractor
"""
import random
import time

from featureforge.experimentation import runner
from sklearn.metrics import roc_auc_score, average_precision_score

from iepy.extraction.fact_extractor import FactExtractorFactory
from iepy.data.db import CandidateEvidenceManager as CEM
import iepy.data.models
from experimentation_utils import result_dict_from_predictions


class NotEnoughLabeledData(Exception):
    pass


class Runner(object):
    def __init__(self):
        self.data = None
        self.relname = None

    def __call__(self, config):
        if u"class_weight" in config[u"classifier_args"]:
            d = config[u"classifier_args"][u"class_weight"]
            assert "true" in d and "false" in d and len(d) == 2
            config[u"classifier_args"][u"class_weight"] = {True: d["true"],
                                                           False: d["false"]}

        # Prepare data
        if self.data is None or self.relname != config["relation"]:
            relation = iepy.data.models.Relation.objects.get(name=config["relation"])
            c_evidences = CEM.candidates_for_relation(relation)
            self.data = CEM.labels_for(relation, c_evidences,
                CEM.conflict_resolution_newest_wins)
            self.data = [(x, label) for x, label in self.data.items() if label is not None]
            self.relname = config["relation"]
        data = self.data
        if not data:
            raise NotEnoughLabeledData("There is no labeled data for training!")
        train, test = get_train_test_indexes(config, len(data))
        train = dict(data[i] for i in train)
        test_evidences, test_labels = zip(*[data[i] for i in test])

        result = {
            "train_size": len(train),
            "test_size": len(test),
            "dataset_size": len(data),
            "start_time": time.time(),
        }

        # Train
        extractor = FactExtractorFactory(config, train)

        # Evaluate prediction
        predicted_labels = extractor.predict(test_evidences)
        result.update(result_dict_from_predictions(
            test_evidences, test_labels, predicted_labels))

        # Evaluate ranking
        predicted_scores = extractor.decision_function(test_evidences)
        auroc = roc_auc_score(test_labels, predicted_scores)
        avgprec = average_precision_score(test_labels, predicted_scores)

        result.update({
            "auROC": auroc,
            "average_precision": avgprec,
        })
        return result


def get_train_test_indexes(config, N):
    r = random.Random()
    r.seed(config[u"data_shuffle_seed"])
    indexes = list(range(N))
    r.shuffle(indexes)
    n = int(config[u"train_percentage"] * N)
    return indexes[:n], indexes[n:]


def extender(config):
    config["features"] = set(config["features"])
    # Add a database id/hash
    dbhash = (iepy.data.models.TextSegment.objects.count(),
              iepy.data.models.IEDocument.objects.count(),
              iepy.data.models.Entity.objects.count())
    config["database_hash"] = dbhash
    return config


if __name__ == '__main__':
    import logging

    logging.basicConfig(
        level=logging.DEBUG,
        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    runner.main(Runner(), extender, booking_duration=1)
