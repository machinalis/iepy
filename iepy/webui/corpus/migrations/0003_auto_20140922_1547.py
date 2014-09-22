# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_auto_20140918_1733'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='labeledrelationevidence',
            options={'ordering': ['segment_id', 'relation_id', 'left_entity_occurrence', 'right_entity_occurrence']},
        ),
        migrations.AlterField(
            model_name='labeledrelationevidence',
            name='label',
            field=models.CharField(choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')], max_length=2, default='SK', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='labeledrelationevidence',
            unique_together=set([('left_entity_occurrence', 'right_entity_occurrence', 'relation', 'segment')]),
        ),
    ]
