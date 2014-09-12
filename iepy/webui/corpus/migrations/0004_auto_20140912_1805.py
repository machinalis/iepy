# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0003_auto_20140912_1755'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entity',
            options={'ordering': ['kind', 'key']},
        ),
        migrations.RemoveField(
            model_name='entity',
            name='canonical_form',
        ),
    ]
