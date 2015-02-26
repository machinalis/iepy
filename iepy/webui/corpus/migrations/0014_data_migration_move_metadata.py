# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db.models import Q
from django.db import models, migrations

import jsonfield.fields


def move_metadata(apps, schema_editor):
    IEDocument = apps.get_model('corpus', 'IEDocument')
    IEDocumentMetadata = apps.get_model('corpus', 'IEDocumentMetadata')

    documents = IEDocument.objects.filter(
        Q(metadata__isnull=False) | Q(title__isnull=False) | Q(url__isnull=False)
    )
    for document in documents:
        metadata = IEDocumentMetadata(
            title=document.title,
            url=document.url,
            metadata=document.metadata,
            document=document
        )
        metadata.save()


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0013_create_metadata_model'),
    ]

    operations = [
        migrations.RunPython(move_metadata),
    ]
