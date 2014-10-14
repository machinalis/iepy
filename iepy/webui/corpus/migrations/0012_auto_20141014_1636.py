# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0011_auto_20141010_1851'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segmenttotag',
            name='creation_date',
        ),
        migrations.AddField(
            model_name='segmenttotag',
            name='modification_date',
            field=models.DateTimeField(default=datetime.date(2014, 10, 14), auto_now=True),
            preserve_default=False,
        ),
    ]
