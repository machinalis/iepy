# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def create_separated_evidence_labels(apps, schema_editor):
    EvidenceCandidate = apps.get_model('corpus', 'EvidenceCandidate')
    EvidenceLabel = apps.get_model('corpus', 'EvidenceLabel')
    for ev in EvidenceCandidate.objects.all():
        EvidenceLabel.objects.create(evidence_candidate=ev,
                                     judge=ev.judge,
                                     label=ev.label,
                                     modification_date=ev.modification_date,
                                     labeled_by_machine=False
                                     )


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0008_add_evidence_label_model'),
    ]

    operations = [
        migrations.RunPython(create_separated_evidence_labels),
    ]
