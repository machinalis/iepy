# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0006_auto_20140929_1655'),
    ]

    operations = [
        migrations.RenameModel(old_name='LabeledRelationEvidence',
                               new_name='EvidenceCandidate'),
    ]
