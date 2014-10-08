from iepy.data.models import Relation, EntityKind


if __name__ == "__main__":
    person = EntityKind.objects.get_or_create(name="PERSON")[0]
    date = EntityKind.objects.get_or_create(name="DATE")[0]
    Relation.objects.get_or_create(name="BIRTHDATE", left_entity_kind=person, right_entity_kind=date)
