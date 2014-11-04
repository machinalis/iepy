# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


DONTKNOW = "DK"
SKIP = "SK"

def replace_dont_know_for_skip(apps, schema_editor):
    EvidenceLabel = apps.get_model('corpus', 'EvidenceLabel')
    for ev in EvidenceLabel.objects.all():
        if ev.label == DONTKNOW:
            ev.label = SKIP
            ev.save()


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0001_squashed_0014_remove_segmenttotag_run_number'),
    ]

    operations = [
        migrations.RunPython(replace_dont_know_for_skip),
    ]
