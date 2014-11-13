# -*- coding: utf-8 -*-

import time


def result_dict_from_predictions(evidences, real_labels, predictions):
    correct = []
    incorrect = []
    tp, fp, tn, fn = 0.0, 0.0, 0.0, 0.0
    for evidence, real, predicted in zip(evidences, real_labels, predictions):
        if real == predicted:
            correct.append(evidence.id)
            if real:
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
    result = {
        "true_positives": tp,
        "false_positives": fp,
        "true_negatives": tn,
        "false_negatives": fn,
        "accuracy": (tp + tn) / len(evidences),
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "end_time": time.time()
    }
    return result
