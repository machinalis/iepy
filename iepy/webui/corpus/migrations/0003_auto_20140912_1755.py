# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0002_auto_20140910_1912'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='entityoccurrence',
            unique_together=set([('entity', 'document', 'offset', 'offset_end')]),
        ),
    ]
