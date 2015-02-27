# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.db.models import Q
from django.db import models, migrations


logging.basicConfig(format="%(asctime)-15s  %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


def move_metadata(apps, schema_editor):
    IEDocument = apps.get_model('corpus', 'IEDocument')
    IEDocumentMetadata = apps.get_model('corpus', 'IEDocumentMetadata')

    documents = IEDocument.objects.filter(
        Q(metadata__isnull=False) | Q(title__isnull=False) | Q(url__isnull=False)
    )
    total = documents.count()
    objects_to_create = []
    for i, document in enumerate(documents.iterator()):
        if i % 1000 == 0:
            logger.info("Created {} out of {}".format(i, total))
            IEDocumentMetadata.objects.bulk_create(objects_to_create)
            objects_to_create = []

        objects_to_create.append(IEDocumentMetadata(
            title=document.title,
            url=document.url,
            items=document.metadata,
            document=document
        ))

    if objects_to_create:
        logger.info("Created {} out of {}".format(i+1, total))
        IEDocumentMetadata.objects.bulk_create(objects_to_create)


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0013_create_metadata_model'),
    ]

    operations = [
        migrations.RunPython(move_metadata),
    ]
