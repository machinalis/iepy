# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0009_auto_20141209_2016'),
    ]

    operations = [
        migrations.AddField(
            model_name='evidencelabel',
            name='relation',
            field=models.ForeignKey(related_name='relation_labels', default=None, to='corpus.Relation', null=True, blank=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='evidencelabel',
            unique_together=set([('evidence_candidate', 'label', 'judge', 'relation')]),
        )
    ]
