# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


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
            model_name='iedocumentmetadata',
            name='document_tmp',
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
            model_name='iedocument',
            name='metadata_fk',
            field=models.OneToOneField(to='corpus.IEDocumentMetadata', related_name='document'),
            preserve_default=True,
        ),
    ]
