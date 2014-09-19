from iepy.data.models import LabeledRelationEvidence as LRE
from .factories import (RelationFactory, EntityFactory, EntityKindFactory,
                        TextSegmentFactory,
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
        self.k_person = EntityKindFactory(name='person')
        self.k_location = EntityKindFactory(name='location')
        self.k_org = EntityKindFactory(name='organization')
        self.john = EntityFactory(key='john', kind=self.k_person)
        self.peter = EntityFactory(key='peter', kind=self.k_person)
        self.london = EntityFactory(key='london', kind=self.k_location)
        self.roma = EntityFactory(key='roma', kind=self.k_location)
        self.UN = EntityFactory(key='United Nations', kind=self.k_org)
        self.WHO = EntityFactory(key='World Health Organization', kind=self.k_org)

        self.r_lives_in = RelationFactory(left_entity_kind=self.k_person,
                                          right_entity_kind=self.k_location)
        self.r_father_of = RelationFactory(left_entity_kind=self.k_person,
                                           right_entity_kind=self.k_person)
        self.weak_label = LRE.DONTKNOW  # means that will need to be re-labeled
        self.solid_label = LRE.YESRELATION

    def create_occurrence(self, doc, e, offset, end):
        return EntityOccurrenceFactory(document=doc, entity=e,
                                       offset=offset, offset_end=end)

    def segment_with_occurrences_factory(self, occurrences=tuple(), **kwargs):
        #occurrences = kwargs.pop('', [])
        s = TextSegmentFactory(**kwargs)
        for occurrence_data in occurrences:
            if isinstance(occurrence_data, (list, tuple)):
                e, start, end = occurrence_data
            else:
                e = occurrence_data
                start, end = 0, 1  # just something, the simplest
            eo = self.create_occurrence(s.document, e, start, end)
            s.entity_occurrences.add(eo)
        return s

    def test_if_no_segment_around_None_is_returned(self):
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())

    def test_if_segments_exists_but_with_no_matching_occurrences_None(self):
        self.segment_with_occurrences_factory()  # No occurrences at all
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())
        self.segment_with_occurrences_factory([self.john])
        self.segment_with_occurrences_factory([self.roma])
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())
        self.segment_with_occurrences_factory([self.john, self.WHO])
        self.segment_with_occurrences_factory([self.roma, self.WHO])
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())
        self.segment_with_occurrences_factory([self.john, self.peter])
        self.segment_with_occurrences_factory([self.roma, self.london])
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())

    def test_if_matching_kinds_is_retrieved(self):
        s = self.segment_with_occurrences_factory([self.john, self.roma])
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_several_of_the_matching_kinds_is_still_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.peter, self.roma])
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_matching_and_other_kinds_is_still_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.roma, self.UN])
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_segment_with_lowest_id_is_retrieved(self):
        s1 = self.segment_with_occurrences_factory([self.john, self.roma])
        self.segment_with_occurrences_factory([self.peter, self.london])
        self.assertEqual(s1, self.r_lives_in.get_next_segment_to_label())

    def test_relation_of_same_kind_expect_at_least_2_of_them(self):
        self.segment_with_occurrences_factory([self.john])
        self.segment_with_occurrences_factory([self.peter, self.london, self.WHO])
        self.assertIsNone(self.r_father_of.get_next_segment_to_label())
        s = self.segment_with_occurrences_factory([self.john, self.peter])
        self.assertEqual(s, self.r_father_of.get_next_segment_to_label())

    def test_relation_of_same_kind_accepts_2_occurrences_of_same_entity(self):
        s = self.segment_with_occurrences_factory([self.john, (self.john, 2, 3)])
        self.assertEqual(s, self.r_father_of.get_next_segment_to_label())

    def test_if_segment_has_all_questions_answered_is_omitted(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.solid_label
            evidence.save()
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_question_labeled_with_dont_know_is_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.weak_label
            evidence.save()
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_some_questions_answered_but_other_dont_know_is_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.peter, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence, lbl in zip(s.get_labeled_evidences(self.r_lives_in),
                                 [self.weak_label, self.solid_label]):
            evidence.label = lbl
            evidence.save()
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_segments_with_zero_evidence_labeled_are_prefered(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.weak_label
            evidence.save()
        # so, this segment is found when searching...
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())
        # But if a new one appears, pristine, with no evidences, is preferred
        s2 = self.segment_with_occurrences_factory([self.peter, self.london])
        self.assertEqual(s2, self.r_lives_in.get_next_segment_to_label())
