# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0004_auto_20140912_1805'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='textsegment',
            options={'ordering': ['document', 'offset', 'offset_end']},
        ),
        migrations.RemoveField(
            model_name='textsegment',
            name='text',
        ),
        migrations.AlterField(
            model_name='textsegment',
            name='document',
            field=models.ForeignKey(related_name=b'segments', to='corpus.IEDocument'),
        ),
        migrations.AlterUniqueTogether(
            name='textsegment',
            unique_together=set([('document', 'offset', 'offset_end')]),
        ),
    ]
