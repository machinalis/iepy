# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0009_auto_20141209_2016'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='evidencecandidate',
            options={'ordering': ['left_entity_occurrence', 'right_entity_occurrence', 'segment_id']},
        ),
        migrations.AddField(
            model_name='evidencelabel',
            name='relation',
            field=models.ForeignKey(related_name='relation_labels', default=None, to='corpus.Relation'),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='evidencecandidate',
            unique_together=set([('left_entity_occurrence', 'right_entity_occurrence', 'segment')]),
        ),
        migrations.AlterUniqueTogether(
            name='evidencelabel',
            unique_together=set([('evidence_candidate', 'label', 'judge', 'relation')]),
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='relation',
        ),
    ]
