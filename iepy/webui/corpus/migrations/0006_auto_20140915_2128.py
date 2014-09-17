# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0005_auto_20140915_2126'),
    ]

    operations = [
        migrations.AlterField(
            model_name='entityoccurrence',
            name='document',
            field=models.ForeignKey(related_name=b'entity_occurrences', to='corpus.IEDocument'),
        ),
        migrations.AlterField(
            model_name='entityoccurrence',
            name='segments',
            field=models.ManyToManyField(related_name=b'entity_occurrences', to=b'corpus.TextSegment'),
        ),
    ]
