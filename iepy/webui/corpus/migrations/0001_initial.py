# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import corpus.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('key', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ['kind', 'key'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityKind',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityOccurrence',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('offset', models.IntegerField()),
                ('offset_end', models.IntegerField()),
                ('alias', models.CharField(max_length=256)),
            ],
            options={
                'ordering': ['document', 'offset', 'offset_end'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IEDocument',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('human_identifier', models.CharField(max_length=256, unique=True)),
                ('title', models.CharField(max_length=256)),
                ('url', models.URLField()),
                ('text', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('tokens', corpus.fields.ListField()),
                ('offsets_to_text', corpus.fields.ListField()),
                ('postags', corpus.fields.ListField()),
                ('sentences', corpus.fields.ListField()),
                ('tokenization_done_at', models.DateTimeField(blank=True, null=True)),
                ('sentencer_done_at', models.DateTimeField(blank=True, null=True)),
                ('tagging_done_at', models.DateTimeField(blank=True, null=True)),
                ('ner_done_at', models.DateTimeField(blank=True, null=True)),
                ('segmentation_done_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', jsonfield.fields.JSONField(blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LabeledRelationEvidence',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('label', models.CharField(default='SK', max_length=2, choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('judge', models.CharField(max_length=256)),
                ('left_entity_occurrence', models.ForeignKey(to='corpus.EntityOccurrence', related_name='left_evidence_relations')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('left_entity_kind', models.ForeignKey(to='corpus.EntityKind', related_name='left_relations')),
                ('right_entity_kind', models.ForeignKey(to='corpus.EntityKind', related_name='right_relations')),
            ],
            options={
                'ordering': ['name', 'left_entity_kind', 'right_entity_kind'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextSegment',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', primary_key=True, serialize=False)),
                ('offset', models.IntegerField(db_index=True)),
                ('offset_end', models.IntegerField(db_index=True)),
                ('document', models.ForeignKey(to='corpus.IEDocument', related_name='segments')),
            ],
            options={
                'ordering': ['document', 'offset', 'offset_end'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='textsegment',
            unique_together=set([('document', 'offset', 'offset_end')]),
        ),
        migrations.AlterUniqueTogether(
            name='relation',
            unique_together=set([('name', 'left_entity_kind', 'right_entity_kind')]),
        ),
        migrations.AddField(
            model_name='labeledrelationevidence',
            name='relation',
            field=models.ForeignKey(to='corpus.Relation', related_name='evidence_relations'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='labeledrelationevidence',
            name='right_entity_occurrence',
            field=models.ForeignKey(to='corpus.EntityOccurrence', related_name='right_evidence_relations'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='labeledrelationevidence',
            name='segment',
            field=models.ForeignKey(to='corpus.TextSegment'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='entityoccurrence',
            name='document',
            field=models.ForeignKey(to='corpus.IEDocument', related_name='entity_occurrences'),
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
            field=models.ManyToManyField(to='corpus.TextSegment', related_name='entity_occurrences'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='entityoccurrence',
            unique_together=set([('entity', 'document', 'offset', 'offset_end')]),
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
