# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_auto_20140915_2142'),
    ]

    operations = [
        migrations.CreateModel(
            name='LabeledRelationEvidence',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(default=b'SK', max_length=2, choices=[(b'NO', b'No relation present'), (b'YE', b'Yes, relation is present'), (b'DK', b"Don't know if the relation is present"), (b'SK', b'Skipped labeling of this evidence'), (b'NS', b'Evidence is nonsense')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('judge', models.CharField(max_length=256)),
                ('left_entity_occurrence', models.ForeignKey(related_name=b'left_evidence_relations', to='corpus.EntityOccurrence')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=256)),
                ('left_entity_kind', models.ForeignKey(related_name=b'left_relations', to='corpus.EntityKind')),
                ('right_entity_kind', models.ForeignKey(related_name=b'right_relations', to='corpus.EntityKind')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='labeledrelationevidence',
            name='relation',
            field=models.ForeignKey(related_name=b'evidence_relations', to='corpus.Relation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='labeledrelationevidence',
            name='right_entity_occurrence',
            field=models.ForeignKey(related_name=b'right_evidence_relations', to='corpus.EntityOccurrence'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='labeledrelationevidence',
            name='segment',
            field=models.ForeignKey(to='corpus.TextSegment'),
            preserve_default=True,
        ),
    ]
