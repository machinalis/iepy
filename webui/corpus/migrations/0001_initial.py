# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import __builtin__
import jsonfield.fields
import corpus.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(max_length=256)),
                ('canonical_form', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ['kind', 'key', 'canonical_form'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityKind',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=256)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityOccurrence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('offset', models.IntegerField()),
                ('offset_end', models.IntegerField()),
                ('alias', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ['document', 'offset', 'offset_end'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IEDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('human_identifier', models.CharField(unique=True, max_length=256)),
                ('title', models.CharField(max_length=256)),
                ('url', models.URLField()),
                ('text', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('tokens', corpus.fields.ListField()),
                ('offsets_to_text', corpus.fields.ListField()),
                ('postags', corpus.fields.ListField()),
                ('sentences', corpus.fields.ListField()),
                ('preprocess_metadata', jsonfield.fields.JSONField(default=__builtin__.dict)),
                ('metadata', jsonfield.fields.JSONField(default=__builtin__.dict)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
                ('offset', models.IntegerField()),
                ('offset_end', models.IntegerField()),
                ('document', models.ForeignKey(to='corpus.IEDocument')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entityoccurrence',
            name='document',
            field=models.ForeignKey(related_name=b'entity_ocurrences', to='corpus.IEDocument'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entityoccurrence',
            name='entity',
            field=models.ForeignKey(to='corpus.Entity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entityoccurrence',
            name='segments',
            field=models.ManyToManyField(related_name=b'entity_ocurrences', to='corpus.TextSegment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entity',
            name='kind',
            field=models.ForeignKey(to='corpus.EntityKind'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entity',
            unique_together=set([('key', 'kind')]),
        ),
    ]
