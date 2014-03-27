from mongoengine.base import ValidationError

from iepy import models

from .manager_case import ManagerTestCase


class ExtendableKindsTests(ManagerTestCase):
    ManagerClass = models.Entity

    def tearDown(self):
        super(ExtendableKindsTests, self).tearDown()
        models.set_custom_entity_kinds([])  # resets kinds to default only

    def get_invalid_kind(self):
        valid_ids = zip(*models.ENTITY_KINDS)[0]
        non_valid = valid_ids[0] + '_x'
        while non_valid in valid_ids:
            non_valid += non_valid + '_x'
        return non_valid, non_valid.upper()

    def test_kind_is_validated_when_saving(self):
        valid_kind = models.ENTITY_KINDS[0][0]  # id of first kind

        models.Entity.objects.create(key='valid', kind=valid_kind,
                                     canonical_form='valid')
        self.assertEqual(models.Entity.objects.count(), 1)
        invalid_kind = self.get_invalid_kind()
        self.assertRaises(ValidationError, models.Entity.objects.create,
                          key='invalid', kind=invalid_kind[0],
                          canonical_form='invalid')
        # Still only one...
        self.assertEqual(models.Entity.objects.count(), 1)

    def test_new_kinds_can_be_added_programatically(self):
        new_kind = self.get_invalid_kind()
        models.set_custom_entity_kinds([new_kind])
        assert models.Entity.objects.count() == 0
        models.Entity.objects.create(key='new', kind=new_kind[0],
                                     canonical_form='new')
        self.assertEqual(models.Entity.objects.count(), 1)

    def test_setting_empty_list_removes_custom(self):
        new_kind = self.get_invalid_kind()
        models.set_custom_entity_kinds([new_kind])  # added
        models.set_custom_entity_kinds([])  # and now, we expect to remove it
        self.assertRaises(ValidationError, models.Entity.objects.create,
                          key='new', kind=new_kind[0],
                          canonical_form='new')
        self.assertEqual(models.Entity.objects.count(), 0)
