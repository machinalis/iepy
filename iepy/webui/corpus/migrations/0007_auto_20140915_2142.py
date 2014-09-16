# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0006_auto_20140915_2128'),
    ]

    operations = [
        migrations.AlterField(
            model_name='textsegment',
            name='offset',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='textsegment',
            name='offset_end',
            field=models.IntegerField(db_index=True),
        ),
    ]
