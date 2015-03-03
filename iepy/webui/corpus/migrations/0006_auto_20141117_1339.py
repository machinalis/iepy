# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import corpus.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0005_create_default_lemmas'),
    ]

    operations = [
        migrations.AddField(
            model_name='iedocument',
            name='syntactic_sentences',
            field=corpus.fields.ListSyntacticTreeField(default='[]'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iedocument',
            name='syntactic_parsing_done_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
