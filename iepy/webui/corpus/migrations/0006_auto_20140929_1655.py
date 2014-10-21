# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0005_auto_20140923_1502'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='iedocument',
            options={'ordering': ['id']},
        ),
    ]
