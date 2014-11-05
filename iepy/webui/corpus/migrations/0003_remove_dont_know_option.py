# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_data_migration_dont_know_skip_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='evidencelabel',
            name='label',
            preserve_default=True,
            field=models.CharField(
                default='SK',
                null=True,
                max_length=2,
                choices=[
                    ('YE', 'Yes, relation is present'),
                    ('NO', 'No relation present'),
                    ('NS', 'Evidence is nonsense'),
                    ('SK', 'Skipped labeling of this evidence')
                ]
            ),
        ),
    ]
