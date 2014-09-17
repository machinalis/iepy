# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0008_auto_20140916_2246'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='relation',
            options={'ordering': ['name', 'left_entity_kind', 'right_entity_kind']},
        ),
        migrations.AlterUniqueTogether(
            name='relation',
            unique_together=set([('name', 'left_entity_kind', 'right_entity_kind')]),
        ),
    ]
