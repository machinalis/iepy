# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import corpus.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_auto_20141127_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='entityoccurrence',
            name='anaphora',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
