"""
Experiment runner for FactExtractor
"""
import os
import time

from featureforge.experimentation import runner

from iepy.extraction.rules_core import RulesBasedCore
from iepy.data.db import CandidateEvidenceManager as CEM
import iepy.data.models

import experimentation_rules


class NotEnoughLabeledData(Exception):
    pass


class RuleNotFound(Exception):
    pass


class Runner(object):
    def __init__(self):
        self.evidences = []
        self.labels = []
        self.data = None
        self.relation = None
        self.relname = None
        self.rules = self._load_rules()

    def _load_rules(self):
        rules = {}
        for attr_name in dir(experimentation_rules):
            attr = getattr(experimentation_rules, attr_name)
            if hasattr(attr, '__call__'):  # is callable
                if hasattr(attr, "is_rule") and attr.is_rule:
                    rules[attr_name] = attr
        return rules

    def __call__(self, config):
        # Prepare data
        if self.data is None or self.relname != config["relation"]:
            self.relname = config["relation"]
            self.relation = iepy.data.models.Relation.objects.get(name=config["relation"])

            candidates = CEM.candidates_for_relation(self.relation)
            self.data = CEM.labels_for(
                self.relation,
                candidates,
                CEM.conflict_resolution_newest_wins
            )
            self.evidences = []
            self.labels = []
            for evidence, label in self.data.items():
                if label is not None:
                    self.labels.append(label)
                    self.evidences.append(evidence)

        if not self.data:
            raise NotEnoughLabeledData("There is no labeled data for training!")

        result = {
            "dataset_size": len(self.data),
            "start_time": time.time(),
        }

        # Load rules in the config
        if config["rules"] == "<all>":
            rules = self.rules.values()
        else:
            for rule_name in config["rules"]:
                if rule_name not in self.rules.keys():
                    raise RuleNotFound(rule_name)
            rules = [rule for rule_name, rule in self.rules.items()
                     if rule_name in config["rules"]]

        # Run the rule based pipeline
        pipeline = RulesBasedCore(self.relation, self.evidences, rules)
        pipeline.start()
        matched = pipeline.known_facts()

        # Evaluate prediction
        correct = []
        incorrect = []
        tp, fp, tn, fn = 0.0, 0.0, 0.0, 0.0
        for evidence, label in zip(self.evidences, self.labels):
            predicted = matched[evidence]
            if predicted == label:
                if label:
                    tp += 1
                else:
                    tn += 1
            else:
                incorrect.append(evidence.id)
                if predicted:
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
            "accuracy": (tp + tn) / len(self.data),
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "correctly_predicted": correct,
            "incorrectly_predicted": incorrect,
            "end_time": time.time()
        })
        return result


def extender(config):
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
        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    this_file_path = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(this_file_path))

    runner.main(
        Runner(),
        extender,
        booking_duration=1,
        use_git_info_from_path=repo_root,
    )
