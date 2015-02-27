# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0012_remove_evidence_candidate_relation_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='IEDocumentMetadata',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(max_length=256, blank=True)),
                ('url', models.URLField(blank=True)),
                ('items', jsonfield.fields.JSONField(blank=True)),
                ('document_tmp', models.ForeignKey(to='corpus.IEDocument')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='iedocument',
            name='metadata_fk',
            field=models.OneToOneField(related_name='document', null=True, to='corpus.IEDocumentMetadata'),
            preserve_default=True,
        ),
    ]
