# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0007_rename_candidate_evidence_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='EvidenceLabel',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
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
    ]
