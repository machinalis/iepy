# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import logging

from django.db import models, migrations


logging.basicConfig(format="%(asctime)-15s  %(message)s")
logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

BULK_SIZE = 2500

def move_metadata(apps, schema_editor):
    IEDocument = apps.get_model('corpus', 'IEDocument')
    IEDocumentMetadata = apps.get_model('corpus', 'IEDocumentMetadata')

    documents = IEDocument.objects.all()
    total = documents.count()
    objects_to_create = []
    logger.info("Creating missing documents metadata objects")
    for i, document in enumerate(documents.iterator()):
        if i % BULK_SIZE == 0:
            logger.info("Created {} out of {}".format(i, total))
            if objects_to_create:
                IEDocumentMetadata.objects.bulk_create(objects_to_create)
                objects_to_create = []

        objects_to_create.append(IEDocumentMetadata(
            title=document.title,
            url=document.url,
            items=document.metadata,
            document_tmp=document
        ))

    if objects_to_create:
        logger.info("Created {} out of {}".format(i+1, total))
        IEDocumentMetadata.objects.bulk_create(objects_to_create)

    logger.info("Updating documents to point to their metadata objects")
    doc_mtds = IEDocumentMetadata.objects.filter(document_tmp__metadata_fk__isnull=True)
    total = doc_mtds.count()
    for i, doc_mtd in enumerate(doc_mtds):
        if i % BULK_SIZE == 0:
            logger.info("Updated {} out of {}".format(i, total))
        IEDocument.objects.filter(pk=doc_mtd.document_tmp_id).update(metadata_fk=doc_mtd.id)
    logger.info("Updated {} out of {}".format(total, total))


class Migration(migrations.Migration):

    dependencies = [
        ('corpus', '0013_create_metadata_model'),
    ]

    operations = [
        migrations.RunPython(move_metadata),
    ]
