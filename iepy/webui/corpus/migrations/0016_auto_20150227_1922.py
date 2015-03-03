# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0015_remove_url_title_metadata_fields'),
    ]

    operations = [
        migrations.RenameField(
            model_name='iedocument',
            old_name='metadata_fk',
            new_name='metadata',
        ),
    ]
