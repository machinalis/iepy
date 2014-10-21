# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0009_data_migration_creating_evidencelabels'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='judge',
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='label',
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='modification_date',
        ),
    ]
