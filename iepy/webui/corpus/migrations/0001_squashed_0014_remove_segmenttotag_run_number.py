# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import corpus.fields


class Migration(migrations.Migration):

    replaces = [('corpus', '0001_initial'), ('corpus', '0002_auto_20140918_1733'), ('corpus', '0003_auto_20140922_1547'), ('corpus', '0004_auto_20140923_1501'), ('corpus', '0005_auto_20140923_1502'), ('corpus', '0006_auto_20140929_1655'), ('corpus', '0007_rename_candidate_evidence_model'), ('corpus', '0008_add_evidence_label_model'), ('corpus', '0009_data_migration_creating_evidencelabels'), ('corpus', '0010_auto_20141009_2027'), ('corpus', '0011_auto_20141010_1851'), ('corpus', '0012_auto_20141014_1636'), ('corpus', '0013_auto_20141014_2136'), ('corpus', '0014_remove_segmenttotag_run_number')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, max_length=256)),
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
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
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
            name='EvidenceCandidate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('left_entity_occurrence', models.ForeignKey(related_name='left_evidence_relations', to='corpus.EntityOccurrence')),
            ],
            options={
                'ordering': ['segment_id', 'relation_id', 'left_entity_occurrence', 'right_entity_occurrence'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EvidenceLabel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('label', models.CharField(default='SK', choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')], null=True, max_length=2)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('judge', models.CharField(max_length=256)),
                ('labeled_by_machine', models.BooleanField(default=True)),
                ('evidence_candidate', models.ForeignKey(related_name='labels', to='corpus.EvidenceCandidate')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IEDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('human_identifier', models.CharField(unique=True, max_length=256)),
                ('title', models.CharField(max_length=256)),
                ('url', models.URLField()),
                ('text', models.TextField()),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('tokens', corpus.fields.ListField()),
                ('offsets_to_text', corpus.fields.ListField()),
                ('postags', corpus.fields.ListField()),
                ('sentences', corpus.fields.ListField()),
                ('tokenization_done_at', models.DateTimeField(null=True, blank=True)),
                ('sentencer_done_at', models.DateTimeField(null=True, blank=True)),
                ('tagging_done_at', models.DateTimeField(null=True, blank=True)),
                ('ner_done_at', models.DateTimeField(null=True, blank=True)),
                ('segmentation_done_at', models.DateTimeField(null=True, blank=True)),
                ('metadata', jsonfield.fields.JSONField(blank=True)),
            ],
            options={
                'ordering': ['id'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=256)),
                ('left_entity_kind', models.ForeignKey(related_name='left_relations', to='corpus.EntityKind')),
                ('right_entity_kind', models.ForeignKey(related_name='right_relations', to='corpus.EntityKind')),
            ],
            options={
                'ordering': ['name', 'left_entity_kind', 'right_entity_kind'],
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SegmentToTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('done', models.BooleanField(default=False)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('relation', models.ForeignKey(to='corpus.Relation')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextSegment',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('offset', models.IntegerField(db_index=True)),
                ('offset_end', models.IntegerField(db_index=True)),
                ('document', models.ForeignKey(related_name='segments', to='corpus.IEDocument')),
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
        migrations.AddField(
            model_name='segmenttotag',
            name='segment',
            field=models.ForeignKey(to='corpus.TextSegment'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='segmenttotag',
            unique_together=set([('segment', 'relation')]),
        ),
        migrations.AlterUniqueTogether(
            name='relation',
            unique_together=set([('name', 'left_entity_kind', 'right_entity_kind')]),
        ),
        migrations.AlterUniqueTogether(
            name='evidencelabel',
            unique_together=set([('evidence_candidate', 'label', 'judge')]),
        ),
        migrations.AddField(
            model_name='evidencecandidate',
            name='relation',
            field=models.ForeignKey(related_name='evidence_relations', to='corpus.Relation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evidencecandidate',
            name='right_entity_occurrence',
            field=models.ForeignKey(related_name='right_evidence_relations', to='corpus.EntityOccurrence'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='evidencecandidate',
            name='segment',
            field=models.ForeignKey(related_name='evidence_relations', to='corpus.TextSegment'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='evidencecandidate',
            unique_together=set([('left_entity_occurrence', 'right_entity_occurrence', 'relation', 'segment')]),
        ),
        migrations.AddField(
            model_name='entityoccurrence',
            name='document',
            field=models.ForeignKey(related_name='entity_occurrences', to='corpus.IEDocument'),
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
            field=models.ManyToManyField(related_name='entity_occurrences', to='corpus.TextSegment'),
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
