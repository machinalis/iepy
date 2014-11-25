# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_gazetteitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='entity',
            name='gazette',
            field=models.ForeignKey(null=True, blank=True, to='corpus.GazetteItem'),
            preserve_default=True,
        ),
    ]
