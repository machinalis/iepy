"""
Experiment runner for ActiveLearningCore
"""
import time

from featureforge.experimentation import runner
from sklearn.metrics import roc_auc_score, average_precision_score

from iepy.extraction.active_learning_core import ActiveLearningCore
from iepy.data.db import CandidateEvidenceManager as CEM
import iepy.data.models
from experimentation_utils import result_dict_from_predictions


class NotEnoughData(Exception):
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
        testset = {x: label for x, label in data}
        candidate_evidences = {x: None for x, _ in data}
        if not data:
            raise NotEnoughData("There is no labeled data for training")
        oracle_answers = config["oracle_answers"]
        N = len(data)
        M = N - oracle_answers  # test set size
        if M / N < 0.1:  # if there ir less than 10% left for testing
            raise NotEnoughData("There is not enough data for evaluation")

        result = {
            "train_size": oracle_answers,
            "test_size": M,
            "dataset_size": N,
            "start_time": time.time(),
        }

        # Interact with oracle
        alcore = ActiveLearningCore(config["relation"], candidate_evidences,
                                    extractor_config=config)
        alcore.start()
        # ^ Is acainst creenhouse emissions
        for _ in range(oracle_answers):
            q = alcore.questions[0]
            alcore.add_answer(q, testset[q])
            del testset[q]  # Once given for training cannot be part of testset
            alcore.process()

        test_evidences, test_labels = zip(*list(testset.items()))
        extractor = alcore.relation_classifier

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


def extender(config):
    config["sparse_features"] = set(config["sparse_features"])
    config["dense_features"] = set(config["dense_features"])
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

    runner.main(Runner(), extender, booking_duration=10 * 60)  # 10 minutes
