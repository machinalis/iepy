from .factories import (RelationFactory, EntityKindFactory, IEDocFactory, TextSegmentFactory,
                        EntityOccurrenceFactory)
from .manager_case import ManagerTestCase


class TestRelations(ManagerTestCase):

    def test_cant_change_kinds_after_creation(self):
        r = RelationFactory()
        new_ek = EntityKindFactory()
        r.left_entity_kind = new_ek
        self.assertRaises(ValueError, r.save)


class TestReferenceBuilding(ManagerTestCase):

    def setUp(self):
        self.doc = IEDocFactory()
        self.r = RelationFactory()

    def create_occurrence(self, e, offset, end):
        return EntityOccurrenceFactory(document=self.d, entity=e,
                                       offset=offset, offset_end=end)

    def test_segment_with_lowest_id_is_retrieved(self):
        pass
