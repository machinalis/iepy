from .factories import RelationFactory, EntityKindFactory
from .manager_case import ManagerTestCase


class TestRelations(ManagerTestCase):

    def test_cant_change_kinds_after_creation(self):
        r = RelationFactory()
        new_ek = EntityKindFactory()
        r.left_entity_kind = new_ek
        self.assertRaises(ValueError, r.save)
