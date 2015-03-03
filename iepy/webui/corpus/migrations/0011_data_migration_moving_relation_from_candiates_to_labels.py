# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.db import models, migrations

logging.basicConfig(format="%(asctime)-15s  %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


def get_key(evidence):
    return (
        evidence.left_entity_occurrence_id,
        evidence.right_entity_occurrence_id,
        evidence.segment_id,
    )


def move_relation_to_labels(apps, schema_editor):
    EvidenceCandidate = apps.get_model('corpus', 'EvidenceCandidate')

    candidates_that_live = {}

    labeled_evidences = EvidenceCandidate.objects.filter(labels__isnull=False)
    labeled_evidences = labeled_evidences.prefetch_related('labels')
    labeled_evidences = labeled_evidences.select_related('relation')
    total = labeled_evidences.count()
    candidates_to_delete = []
    for i, candidate_to_check in enumerate(labeled_evidences):
        if i % 1000 == 0:
            logger.info("Checking {} out of {}".format(i, total))

        key = get_key(candidate_to_check)
        if key in candidates_that_live:
            live_candidate = candidates_that_live.get(key)
            candidate_to_check.labels.all().update(evidence_candidate=live_candidate,
                                                   relation=candidate_to_check.relation)
            candidates_to_delete.append(candidate_to_check.id)
        else:
            candidates_that_live[key] = candidate_to_check
            # Set the relation of every label of the candidate
            candidate_to_check.labels.all().update(relation=candidate_to_check.relation)

    not_labeled_evidences = EvidenceCandidate.objects.filter(labels__isnull=True)
    not_labeled_evidences = not_labeled_evidences.values_list(
        'left_entity_occurrence_id', 'right_entity_occurrence_id', 'segment_id', 'id')

    total = not_labeled_evidences.count()
    logger.info("Needing to check {} unlabeled candidate evidences".format(total))
    keys_taken = set(candidates_that_live.keys())
    for i, (leoid, reoid, sid, c_id) in enumerate(not_labeled_evidences.iterator()):
        key = (leoid, reoid, sid)

        if i % 1000 == 0:
            logger.info("Checking {} out of {}".format(i, total))
        if key in keys_taken:
            candidates_to_delete.append(c_id)
        else:
            keys_taken.add(key)

    EvidenceCandidate.objects.filter(pk__in=candidates_to_delete).all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0010_auto_20150219_1752'),
    ]

    operations = [
        migrations.RunPython(move_relation_to_labels),
    ]
