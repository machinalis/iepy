# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0006_auto_20140929_1655'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvidenceCandidate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('left_entity_occurrence', models.ForeignKey(to='corpus.EntityOccurrence', related_name='left_evidence_relations')),
                ('relation', models.ForeignKey(to='corpus.Relation', related_name='evidence_relations')),
                ('right_entity_occurrence', models.ForeignKey(to='corpus.EntityOccurrence', related_name='right_evidence_relations')),
                ('segment', models.ForeignKey(to='corpus.TextSegment', related_name='evidence_relations')),
            ],
            options={
                'abstract': False,
                'ordering': ['segment_id', 'relation_id', 'left_entity_occurrence', 'right_entity_occurrence'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EvidenceLabel',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('label', models.CharField(default='SK', null=True, max_length=2, choices=[('NO', 'No relation present'), ('YE', 'Yes, relation is present'), ('DK', "Don't know if the relation is present"), ('SK', 'Skipped labeling of this evidence'), ('NS', 'Evidence is nonsense')])),
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
            name='labeledrelationevidence',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='labeledrelationevidence',
            name='left_entity_occurrence',
        ),
        migrations.RemoveField(
            model_name='labeledrelationevidence',
            name='relation',
        ),
        migrations.RemoveField(
            model_name='labeledrelationevidence',
            name='right_entity_occurrence',
        ),
        migrations.RemoveField(
            model_name='labeledrelationevidence',
            name='segment',
        ),
        migrations.DeleteModel(
            name='LabeledRelationEvidence',
        ),
        migrations.AlterUniqueTogether(
            name='evidencecandidate',
            unique_together=set([('left_entity_occurrence', 'right_entity_occurrence', 'relation', 'segment')]),
        ),
    ]
