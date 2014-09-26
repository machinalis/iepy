from unittest import mock
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


class BaseTestReferenceBuilding(ManagerTestCase):
    # Reference = a complete labeled Corpus

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
        self.r_was_born_in = RelationFactory(left_entity_kind=self.k_person,
                                             right_entity_kind=self.k_location)
        self.r_father_of = RelationFactory(left_entity_kind=self.k_person,
                                           right_entity_kind=self.k_person)
        self.weak_label = LRE.DONTKNOW  # means that will need to be re-labeled
        self.solid_label = LRE.YESRELATION

    def create_occurrence(self, doc, e, offset, end):
        return EntityOccurrenceFactory(document=doc, entity=e,
                                       offset=offset, offset_end=end)

    def segment_with_occurrences_factory(self, occurrences=tuple(), **kwargs):
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


class TestReferenceNextSegmentToLabel(BaseTestReferenceBuilding):

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

    # until now, only Entity Kind matching. Let's check about existence and properties
    # of questions - aka Labeled-Evidence

    def test_if_segment_has_all_questions_answered_is_omitted(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.solid_label
            evidence.save()
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_all_questions_answered_for_other_relation_is_NOT_omitted(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence in s.get_labeled_evidences(self.r_was_born_in):
            evidence.label = self.solid_label
            evidence.save()
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_question_not_labeled_is_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = None
            evidence.save()
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_question_labeled_with_dont_know_is_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.weak_label
            evidence.save()
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_was_fully_labeled_but_some_empty_for_other_relation_is_omitted(self):
        # ie, LabeledE Evidences of a Segment with some other relation doesnt matter here.
        # This test is more for ensuring we are not coding an underised side-effect
        s = self.segment_with_occurrences_factory([self.john, self.london])
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.solid_label
            evidence.save()
        for evidence in s.get_labeled_evidences(self.r_was_born_in):
            evidence.label = None
            evidence.save()
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_has_some_questions_answered_but_other_dont_know_is_found(self):
        s = self.segment_with_occurrences_factory([self.john, self.peter, self.london])
        self.assertIsNotNone(self.r_lives_in.get_next_segment_to_label())
        for evidence, lbl in zip(s.get_labeled_evidences(self.r_lives_in),
                                 [self.weak_label, self.solid_label]):
            evidence.label = lbl
            evidence.save()
        self.assertEqual(s, self.r_lives_in.get_next_segment_to_label())

    def test_if_segment_was_fully_labeled_but_some_dunno_for_other_relation_is_omitted(self):
        # ie, LabeledE Evidences of a Segment with some other relation doesnt matter here.
        # This test is more for ensuring we are not coding an underised side-effect
        s = self.segment_with_occurrences_factory([self.john, self.london])
        for evidence in s.get_labeled_evidences(self.r_lives_in):
            evidence.label = self.solid_label
            evidence.save()
        for evidence in s.get_labeled_evidences(self.r_was_born_in):
            evidence.label = self.weak_label
            evidence.save()
        self.assertIsNone(self.r_lives_in.get_next_segment_to_label())

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


class TestNavigateLabeledSegments(BaseTestReferenceBuilding):

    def create_labeled_segments_for_relation(self, relation, how_many):
        result = []
        for i in range(how_many):
            s = self.segment_with_occurrences_factory([self.john, self.london, self.roma])
            result.append(s)
            for le in s.get_labeled_evidences(relation):
                le.label = self.solid_label
                le.save()
        return result

    def test_asking_neighbor_when_nothing_is_labeled_returns_None(self):
        segm = TextSegmentFactory()
        self.assertIsNone(self.r_lives_in.labeled_neighbor(segm))

    def test_labeled_evidences_for_other_relations_doesnt_affect(self):
        segm = TextSegmentFactory()
        self.create_labeled_segments_for_relation(self.r_father_of, 5)
        self.assertIsNone(self.r_lives_in.labeled_neighbor(segm))

    def test_asking_previous_returns_low_closest_segment_with_labeled_evidences(self):
        r = self.r_lives_in
        segments = self.create_labeled_segments_for_relation(r, 5)
        reference = segments[2]  # the one in the middle
        prev_id = r.labeled_neighbor(reference, back=True)
        self.assertEqual(prev_id, segments[1].id)
        # But if that had no labeled evidences...
        segments[1].evidence_relations.all().delete()
        prev_id = r.labeled_neighbor(reference, back=True)
        self.assertEqual(prev_id, segments[0].id)

    def test_segments_with_all_empty_answers_are_excluded(self):
        # Because they have zero actual labels
        r = self.r_lives_in
        segments = self.create_labeled_segments_for_relation(r, 5)
        reference = segments[2]  # the one in the middle
        seg_1_evidences = list(segments[1].get_labeled_evidences(r))
        assert len(seg_1_evidences) > 1
        seg_1_evidences[0].label = None
        seg_1_evidences[0].save()
        # some none, not all, still found
        self.assertEqual(segments[1].id,
                         r.labeled_neighbor(reference, back=True))
        for le in seg_1_evidences:
            le.label = None
            le.save()
        # all none, not found
        self.assertNotEqual(segments[1].id,
                            r.labeled_neighbor(reference, back=True))
        self.assertEqual(segments[0].id,
                         r.labeled_neighbor(reference, back=True))

    def test_all_labels_empty_for_this_relation_but_filled_for_other_still_omitted(self):
        r = self.r_lives_in
        segments = self.create_labeled_segments_for_relation(r, 5)
        reference = segments[2]  # the one in the middle
        for le in segments[1].get_labeled_evidences(r):
            le.label = None
            le.save()
        # all none for relation "r_lives_in", shall be not found
        for le in segments[1].get_labeled_evidences(self.r_father_of):
            le.label = self.solid_label
            le.save()
        self.assertNotEqual(segments[1].id,
                            r.labeled_neighbor(reference, back=True))

    def test_asking_next_returns_high_closest_segment_with_labeled_evidences(self):
        r = self.r_lives_in
        segments = self.create_labeled_segments_for_relation(r, 5)
        reference = segments[2]  # the one in the middle
        next_id = r.labeled_neighbor(reference, back=False)
        self.assertEqual(next_id, segments[3].id)
        # But if that had no labeled evidences...
        segments[3].evidence_relations.all().delete()
        next_id = r.labeled_neighbor(reference, back=False)
        self.assertEqual(next_id, segments[4].id)

    def test_asking_for_neighbor_of_unlabeled_segment_returns_last_available(self):
        r = self.r_lives_in
        segments = self.create_labeled_segments_for_relation(r, 5)
        s = self.segment_with_occurrences_factory()
        expected = segments[-1].id
        self.assertEqual(expected, r.labeled_neighbor(s, back=True))
        self.assertEqual(expected, r.labeled_neighbor(s, back=False))


class TestReferenceNextDocumentToLabel(BaseTestReferenceBuilding):

    def setUp(self):
        super().setUp()
        self.relation = self.r_lives_in
        self.eo1, self.eo2 = self.john, self.roma
        patcher = mock.patch.object(self.relation, 'get_next_segment_to_label')
        self.mock_next_segment = patcher.start()
        self.addCleanup(patcher.stop)
        self.mock_next_segment.return_value = None

    def test_if_no_segment_returned_then_no_document_returned(self):
        self.assertEqual(self.relation.get_next_document_to_label(), None)
        self.mock_next_segment.assert_called_once_with()

    def test_if_segment_returned_then_its_document_is_returned(self):
        s = self.segment_with_occurrences_factory([self.eo1, self.eo2])
        self.mock_next_segment.return_value = s
        self.assertEqual(self.relation.get_next_document_to_label(), s.document)
        self.mock_next_segment.assert_called_once_with()
