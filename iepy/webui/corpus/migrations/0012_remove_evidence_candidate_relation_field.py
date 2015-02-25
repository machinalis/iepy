# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0011_data_migration_moving_relation_from_candiates_to_labels'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evidencecandidate',
            options={'ordering': ['left_entity_occurrence', 'right_entity_occurrence', 'segment_id']},
        ),
        migrations.AlterUniqueTogether(
            name='evidencecandidate',
            unique_together=set([('left_entity_occurrence', 'right_entity_occurrence', 'segment')]),
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='relation',
        ),
    ]
