# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0016_auto_20150227_1922'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iedocument',
            name='metadata',
            field=models.OneToOneField(related_name='document', on_delete=django.db.models.deletion.PROTECT, to='corpus.IEDocumentMetadata'),
            preserve_default=True,
        ),
    ]
