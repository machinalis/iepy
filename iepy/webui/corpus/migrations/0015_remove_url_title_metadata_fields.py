# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0014_data_migration_move_metadata'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='iedocument',
            name='metadata',
        ),
        migrations.RemoveField(
            model_name='iedocument',
            name='title',
        ),
        migrations.RemoveField(
            model_name='iedocument',
            name='url',
        ),
        migrations.AlterField(
            model_name='iedocumentmetadata',
            name='document',
            field=models.OneToOneField(to='corpus.IEDocument', related_name='metadata'),
            preserve_default=True,
        ),
    ]
