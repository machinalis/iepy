# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labeledrelationevidence',
            name='segment',
            field=models.ForeignKey(to='corpus.TextSegment', related_name='evidence_relations'),
        ),
    ]
