# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0013_auto_20141014_2136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='segmenttotag',
            name='run_number',
        ),
    ]
