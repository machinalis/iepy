# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0006_auto_20141117_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='GazetteItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('text', models.CharField(unique=True, max_length=256)),
                ('from_freebase', models.CharField(max_length=256)),
                ('kind', models.ForeignKey(to='corpus.EntityKind')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='entity',
            name='gazette',
            field=models.ForeignKey(blank=True, to='corpus.GazetteItem', null=True, on_delete=django.db.models.deletion.SET_NULL),
            preserve_default=True,
        ),
    ]
