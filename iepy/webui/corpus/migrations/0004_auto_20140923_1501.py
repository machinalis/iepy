# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0003_auto_20140922_1547'),
    ]

    operations = [
        migrations.AlterField(
            model_name='labeledrelationevidence',
            name='date',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
