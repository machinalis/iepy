# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0004_auto_20140923_1501'),
    ]

    operations = [
        migrations.RenameField(
            model_name='labeledrelationevidence',
            old_name='date',
            new_name='modification_date',
        ),
    ]
