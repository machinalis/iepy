# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import corpus.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0003_remove_dont_know_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='iedocument',
            name='lemmas',
            field=corpus.fields.ListField(default='[]'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='iedocument',
            name='lemmatization_done_at',
            field=models.DateTimeField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
