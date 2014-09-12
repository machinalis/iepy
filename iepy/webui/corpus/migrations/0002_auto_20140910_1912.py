# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import __builtin__
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='iedocument',
            old_name='ner',
            new_name='ner_done_at',
        ),
        migrations.RenameField(
            model_name='iedocument',
            old_name='segmentation',
            new_name='segmentation_done_at',
        ),
        migrations.RenameField(
            model_name='iedocument',
            old_name='tagging',
            new_name='tagging_done_at',
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='metadata',
            field=jsonfield.fields.JSONField(default=__builtin__.dict, blank=True),
        ),
    ]
