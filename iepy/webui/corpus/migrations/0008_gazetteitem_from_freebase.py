# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_gazetteitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='gazetteitem',
            name='from_freebase',
            field=models.CharField(default='', max_length=256, unique=True),
            preserve_default=False,
        ),
    ]
