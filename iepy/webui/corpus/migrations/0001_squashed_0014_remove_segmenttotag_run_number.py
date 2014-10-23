# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields
import datetime
import corpus.fields


# Functions from the following migrations need manual copying.
# Move them and any dependencies into this file, then update the
# RunPython operations to refer to the local versions:
# corpus.migrations.0009_data_migration_creating_evidencelabels
def copied__create_separated_evidence_labels(apps, schema_editor):
    # function copied from migration 0009_data_migration_creating_evidencelabels
    EvidenceCandidate = apps.get_model('corpus', 'EvidenceCandidate')
    EvidenceLabel = apps.get_model('corpus', 'EvidenceLabel')
    for ev in EvidenceCandidate.objects.all():
        EvidenceLabel.objects.create(evidence_candidate=ev,
                                     judge=ev.judge,
                                     label=ev.label,
                                     modification_date=ev.modification_date,
                                     labeled_by_machine=False
                                     )



class Migration(migrations.Migration):

    replaces = [('corpus', '0001_initial'), ('corpus', '0002_auto_20140918_1733'), ('corpus', '0003_auto_20140922_1547'), ('corpus', '0004_auto_20140923_1501'), ('corpus', '0005_auto_20140923_1502'), ('corpus', '0006_auto_20140929_1655'), ('corpus', '0007_rename_candidate_evidence_model'), ('corpus', '0008_add_evidence_label_model'), ('corpus', '0009_data_migration_creating_evidencelabels'), ('corpus', '0010_auto_20141009_2027'), ('corpus', '0011_auto_20141010_1851'), ('corpus', '0012_auto_20141014_1636'), ('corpus', '0013_auto_20141014_2136'), ('corpus', '0014_remove_segmenttotag_run_number')]

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entity',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
                'ordering': ['kind', 'key'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityKind',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
            ],
            options={
                'abstract': False,
                'ordering': ['name'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EntityOccurrence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('offset', models.IntegerField()),
                ('offset_end', models.IntegerField()),
                ('alias', models.CharField(max_length=256)),
            ],
            options={
                'abstract': False,
                'ordering': ['document', 'offset', 'offset_end'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='IEDocument',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('human_identifier', models.CharField(max_length=256, unique=True)),
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
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='LabeledRelationEvidence',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')], default='SK', max_length=2)),
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
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('left_entity_kind', models.ForeignKey(to='corpus.EntityKind', related_name='left_relations')),
                ('right_entity_kind', models.ForeignKey(to='corpus.EntityKind', related_name='right_relations')),
            ],
            options={
                'abstract': False,
                'ordering': ['name', 'left_entity_kind', 'right_entity_kind'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextSegment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('offset', models.IntegerField(db_index=True)),
                ('offset_end', models.IntegerField(db_index=True)),
                ('document', models.ForeignKey(to='corpus.IEDocument', related_name='segments')),
            ],
            options={
                'abstract': False,
                'ordering': ['document', 'offset', 'offset_end'],
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
            field=models.ForeignKey(to='corpus.TextSegment', related_name='evidence_relations'),
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
        migrations.AlterModelOptions(
            name='labeledrelationevidence',
            options={'ordering': ['segment_id', 'relation_id', 'left_entity_occurrence', 'right_entity_occurrence']},
        ),
        migrations.AlterField(
            model_name='labeledrelationevidence',
            name='label',
            field=models.CharField(choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')], default='SK', null=True, max_length=2),
        ),
        migrations.AlterUniqueTogether(
            name='labeledrelationevidence',
            unique_together=set([('left_entity_occurrence', 'right_entity_occurrence', 'relation', 'segment')]),
        ),
        migrations.RenameField(
            model_name='labeledrelationevidence',
            old_name='date',
            new_name='modification_date',
        ),
        migrations.AlterField(
            model_name='labeledrelationevidence',
            name='modification_date',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterModelOptions(
            name='iedocument',
            options={'ordering': ['id']},
        ),
        migrations.RenameModel(
            old_name='LabeledRelationEvidence',
            new_name='EvidenceCandidate',
        ),
        migrations.CreateModel(
            name='EvidenceLabel',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')], default='SK', null=True, max_length=2)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('judge', models.CharField(max_length=256)),
                ('labeled_by_machine', models.BooleanField(default=True)),
                ('evidence_candidate', models.ForeignKey(to='corpus.EvidenceCandidate', related_name='labels')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='evidencelabel',
            unique_together=set([('evidence_candidate', 'label', 'judge')]),
        ),
        migrations.RunPython(
            code=copied__create_separated_evidence_labels,
            reverse_code=None,
            atomic=True,
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='judge',
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='label',
        ),
        migrations.RemoveField(
            model_name='evidencecandidate',
            name='modification_date',
        ),
        migrations.CreateModel(
            name='SegmentToTag',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('run_number', models.IntegerField()),
                ('done', models.BooleanField(default=False)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('relation', models.ForeignKey(to='corpus.Relation')),
                ('segment', models.ForeignKey(to='corpus.TextSegment')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='segmenttotag',
            unique_together=set([('segment', 'relation', 'run_number')]),
        ),
        migrations.RemoveField(
            model_name='segmenttotag',
            name='creation_date',
        ),
        migrations.AddField(
            model_name='segmenttotag',
            name='modification_date',
            field=models.DateTimeField(default=datetime.date(2014, 10, 14), auto_now=True),
            preserve_default=False,
        ),
        migrations.AlterUniqueTogether(
            name='segmenttotag',
            unique_together=set([('segment', 'relation')]),
        ),
        migrations.RemoveField(
            model_name='segmenttotag',
            name='run_number',
        ),
    ]
