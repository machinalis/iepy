from unittest import mock
from django.core.exceptions import ObjectDoesNotExist

from .manager_case import ManagerTestCase
from .factories import (
    IEDocFactory, GazetteItemFactory,
    EntityFactory, EntityKindFactory,
)

from iepy.data.models import GazetteItem, Entity
from iepy.data.db import EntityOccurrenceManager


class TestEntityGazetteRelation(ManagerTestCase):
    def test_delete_entity_removes_gazette_item(self):
        entity = EntityFactory()
        entity.gazette = GazetteItemFactory()
        entity.save()

        gazette_id = entity.gazette.id
        self.assertIsNotNone(GazetteItem.objects.get(pk=gazette_id))
        entity.delete()
        with self.assertRaises(ObjectDoesNotExist):
            GazetteItem.objects.get(pk=gazette_id)

    def test_entity_delete_withou_gazette_works(self):
        entity = EntityFactory()
        self.assertIsNone(entity.gazette)
        entity.delete()

    def test_delete_gazette_removes_entity(self):
        gazette = GazetteItemFactory()
        entity = EntityFactory()
        entity.gazette = gazette
        entity.save()
        gazette.save()

        entity_id = entity.id
        gazette.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Entity.objects.get(pk=entity_id)

    def test_other_entities_are_not_deleted(self):
        gazette = GazetteItemFactory()
        entity1 = EntityFactory()
        entity2 = EntityFactory()

        gazette.save()
        entity1.gazette = gazette
        entity1.save()
        entity2.save()

        entity1_id = entity1.id
        entity2_id = entity2.id
        gazette.delete()
        with self.assertRaises(ObjectDoesNotExist):
            Entity.objects.get(pk=entity1_id)

        try:
            Entity.objects.get(pk=entity2_id)
        except ObjectDoesNotExist:
            self.fail("Entity does not exists and it should")


class TestEntityOccurrenceCreation(ManagerTestCase):
    def test_entity_created(self):
        kind = EntityKindFactory()
        doc = IEDocFactory()
        offset = 0
        offset_end = 1

        entity_count = Entity.objects.all().count()
        EntityOccurrenceManager.create_with_entity(
            kind, doc, offset, offset_end
        )
        new_entity_count = Entity.objects.all().count()
        self.assertEqual(new_entity_count, entity_count + 1)

    def test_segmenter_is_run(self):
        with mock.patch("iepy.preprocess.segmenter.SyntacticSegmenterRunner") as mock_segmenter:
            kind = EntityKindFactory()
            doc = IEDocFactory()
            offset = 0
            offset_end = 1

            EntityOccurrenceManager.create_with_entity(
                kind, doc, offset, offset_end
            )

            self.assertTrue(mock_segmenter.called)
