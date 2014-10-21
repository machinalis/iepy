# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0010_auto_20141009_2027'),
    ]

    operations = [
        migrations.CreateModel(
            name='SegmentToTag',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
    ]
