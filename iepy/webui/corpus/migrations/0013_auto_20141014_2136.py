# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0012_auto_20141014_1636'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='segmenttotag',
            unique_together=set([('segment', 'relation')]),
        ),
    ]
