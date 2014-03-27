from os import environ

from mongoengine.base import ValidationError

from iepy.models import Entity, ENTITY_KINDS, set_custom_entity_kinds, _KINDS_ENV
from .manager_case import ManagerTestCase


class ExtendableKindsTests(ManagerTestCase):
    ManagerClass = Entity

    def tearDown(self):
        super(ExtendableKindsTests, self).tearDown()
        set_custom_entity_kinds([])  # resets kinds to default only

    def get_invalid_kind(self):
        valid_ids = zip(*ENTITY_KINDS)[0]
        non_valid = valid_ids[0] + '_x'
        while non_valid in valid_ids:
            non_valid += non_valid + '_x'
        return non_valid, non_valid.upper()

    def test_kind_is_validated_when_saving(self):
        valid_kind = ENTITY_KINDS[0][0]  # id of first kind

        Entity.objects.create(key='valid', kind=valid_kind,
                              canonical_form='valid')
        self.assertEqual(Entity.objects.count(), 1)
        invalid_kind = self.get_invalid_kind()
        self.assertRaises(ValidationError, Entity.objects.create,
                          key='invalid', kind=invalid_kind[0],
                          canonical_form='invalid')
        # Still only one...
        self.assertEqual(Entity.objects.count(), 1)

    def test_new_kinds_can_be_added_programatically(self):
        new_kind = self.get_invalid_kind()
        set_custom_entity_kinds([new_kind])
        assert Entity.objects.count() == 0
        Entity.objects.create(key='new', kind=new_kind[0],
                              canonical_form='new')
        self.assertEqual(Entity.objects.count(), 1)

    def test_setting_empty_list_removes_custom(self):
        new_kind = self.get_invalid_kind()
        set_custom_entity_kinds([new_kind])  # added
        set_custom_entity_kinds([])  # and now, we expect to remove it
        self.assertRaises(ValidationError, Entity.objects.create,
                          key='new', kind=new_kind[0],
                          canonical_form='new')
        self.assertEqual(Entity.objects.count(), 0)

    def test_custom_kinds_can_be_defined_by_environ_variable(self):
        new_kind = self.get_invalid_kind()
        environ[_KINDS_ENV] = '%s:%s' % tuple(new_kind)
        from iepy import models  # reimported so changes are applied
        mEntity = models.Entity
        assert mEntity.objects.count() == 0
        mEntity.objects.create(key='new', kind=new_kind[0],
                               canonical_form='new')
        self.assertEqual(mEntity.objects.count(), 1)
