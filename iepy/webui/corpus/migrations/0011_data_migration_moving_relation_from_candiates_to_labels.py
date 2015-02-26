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
    total = labeled_evidences.count()
    for i, candidate_to_check in enumerate(labeled_evidences):
        if i % 1000 == 0:
            logger.info("Checking {} out of {}".format(i, total))

        key = get_key(candidate_to_check)
        if key in candidates_that_live:
            live_candidate = candidates_that_live.get(key)
            labels = list(candidate_to_check.labels.all())
            for label in labels:
                label.evidence_candidate = live_candidate
                label.relation = candidate_to_check.relation
                label.save()
            candidate_to_check.delete()
        else:
            candidates_that_live[key] = candidate_to_check
            # Set the relation of every label of the candidate
            for label in candidate_to_check.labels.all():
                label.relation = candidate_to_check.relation
                label.save()

    not_labeled_evidences = EvidenceCandidate.objects.filter(labels__isnull=True)
    total = not_labeled_evidences.count()
    for i, candidate_to_check in enumerate(not_labeled_evidences):
        if i % 1000 == 0:
            logger.info("Checking {} out of {}".format(i, total))
        if key in candidates_that_live:
            candidate_to_check.delete()
        else:
            candidates_that_live[key] = candidate_to_check


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0010_auto_20150219_1752'),
    ]

    operations = [
        migrations.RunPython(move_relation_to_labels),
    ]
