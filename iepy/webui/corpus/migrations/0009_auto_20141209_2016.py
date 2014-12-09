# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import corpus.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0008_auto_20141209_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iedocument',
            name='lemmas',
            field=corpus.fields.ListField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='offsets_to_text',
            field=corpus.fields.ListField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='postags',
            field=corpus.fields.ListField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='sentences',
            field=corpus.fields.ListField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='syntactic_sentences',
            field=corpus.fields.ListSyntacticTreeField(editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='title',
            field=models.CharField(blank=True, max_length=256),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='tokens',
            field=corpus.fields.ListField(blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='iedocument',
            name='url',
            field=models.URLField(blank=True),
            preserve_default=True,
        ),
    ]
