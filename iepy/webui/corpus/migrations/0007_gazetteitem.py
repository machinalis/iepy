# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0006_auto_20141117_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='GazetteItem',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('text', models.CharField(unique=True, max_length=256)),
                ('kind', models.ForeignKey(to='corpus.EntityKind')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]
