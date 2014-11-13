"""
IEPY rules verifier


Usage:
    rules_verifier.py <relation> [options]

Options:
  --shuffle             Chooses the sample randomly and not the first ones
  -r --rule=<rule>      Tests only this rule
  -l --limit=<limit>    Limits the amount of evidences uses
  -h --help             Show this screen
"""

import sys
import logging
from docopt import docopt

import refo
from django.core.exceptions import ObjectDoesNotExist
from colorama import init as colorama_init

import iepy
iepy.setup(__file__)

from iepy.data import models
from iepy.data.db import CandidateEvidenceManager
from iepy.extraction.terminal import TerminalEvidenceFormatter
from iepy.extraction.rules import (
    is_rule, load_rules, generate_subject_and_object,
    generate_tokens_to_match
)
from iepy.metrics import result_dict_from_predictions


logging.basicConfig(level=logging.INFO, format='%(message)s')


def run_from_command_line():
    opts = docopt(__doc__, version=iepy.__version__)
    relation_name = opts.get("<relation>")
    limit = opts.get("--limit")
    rule_name = opts.get("--rule")
    shuffle = opts.get("--shuffle")

    if limit is None:
        limit = -1

    try:
        limit = int(limit)
    except ValueError:
        logging.error("Invalid limit value, it must be a number")
        sys.exit(1)

    try:
        relation = models.Relation.objects.get(name=relation_name)
    except ObjectDoesNotExist:
        logging.error("Relation {!r} not found".format(relation_name))
        sys.exit(1)

    # Load rules
    rules = get_rules(rule_name)

    # Load evidences
    evidences = CandidateEvidenceManager.candidates_for_relation(
        relation, False, seg_limit=limit, shuffle_segs=shuffle
    )
    conflict_solver = CandidateEvidenceManager.conflict_resolution_newest_wins
    answers = CandidateEvidenceManager.labels_for(
        relation, evidences, conflict_solver
    )
    run_tests(rules, evidences, answers)


def run_tests(rules, evidences, answers):
    predictions = []
    real_labels = []
    evidences_with_labels = []

    colorama_init()
    formatter = TerminalEvidenceFormatter()

    for rule in rules:
        title = "Matches for rule '{}' (value: {})".format(
            rule.__name__, rule.answer
        )
        print("\n{}\n{}".format(title, "-" * len(title)))

        anything_matched = False
        for evidence in evidences:
            Subject, Object = generate_subject_and_object(evidence)
            tokens_to_match = generate_tokens_to_match(evidence)

            regex = rule(Subject, Object)
            match = refo.match(regex, tokens_to_match)

            if match:
                anything_matched = True
                print("  * {}".format(formatter.colored_text(evidence)))

            if evidence in answers:
                evidences_with_labels.append(evidence)
                real_labels.append(answers[evidence])

                if match:
                    predictions.append(rule.answer)
                else:
                    predictions.append(False)

        if not anything_matched:
            print("  nothing matched")

        print()

    if real_labels:
        results = result_dict_from_predictions(
            evidences_with_labels, real_labels, predictions
        )
        results.pop("end_time")
        keys = [
            "true_positives", "true_negatives",
            "false_positives", "false_negatives",
            "precision", "recall",
            "accuracy", "f1",
        ]

        title = "Metrics"
        print("{}\n{}".format(title, "-" * len(title)))
        for key in keys:
            print("{:>15}: {:.2f}".format(key, results[key]))


def get_rules(rule_name):
    # Load rules
    if rule_name is None:
        rules = load_rules()
    else:
        try:
            rule = getattr(iepy.instance.rules, rule_name)
        except AttributeError:
            logging.error("rule '{}' does not exists".format(rule_name))
            sys.exit(1)

        if is_rule(rule):
            rules = [rule]
        else:
            logging.error("{} is not a rule".format(rule_name))
            sys.exit(1)

    return rules


if __name__ == "__main__":
    run_from_command_line()
