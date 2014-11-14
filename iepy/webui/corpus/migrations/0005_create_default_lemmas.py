# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def add_default_lemmas(apps, schema_editor):
    Document = apps.get_model('corpus', 'IEDocument')
    for document in Document.objects.all():
        tokens = document.tokens
        document.lemmas = [""] * len(tokens)
        document.save()


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0004_auto_20141113_1715'),
    ]

    operations = [
        migrations.RunPython(add_default_lemmas),
    ]
