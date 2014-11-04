# -*- coding: utf-8 -*-
from unittest import mock

from iepy.data.models import EvidenceCandidate
from iepy.extraction.active_learning_core import ActiveLearningCore
from .factories import EvidenceCandidateFactory, RelationFactory
from .manager_case import ManagerTestCase


class ActiveLearningTestMixin:
    def setUp(self):
        self.relation = RelationFactory(left_entity_kind__name='person',
                                        right_entity_kind__name='location')
        self.ev1 = EvidenceCandidateFactory(relation=self.relation)
        self.ev2 = EvidenceCandidateFactory(relation=self.relation)
        self.ev3 = EvidenceCandidateFactory(relation=self.relation)

    def lbl_evs(self, values):
        return dict(zip(EvidenceCandidate.objects.all().order_by('id'), values))


class TestQuestions(ActiveLearningTestMixin, ManagerTestCase):

    def test_cant_start_core_with_all_evidence_labeled(self):
        # why not? Well, simply because is overkill to ask IEPY something
        # that's already available
        evidences = self.lbl_evs([True, False, True])
        self.assertRaises(ValueError, ActiveLearningCore,
                          self.relation, evidences
                          )

    def test_every_evidence_without_label_is_a_question(self):
        c = ActiveLearningCore(self.relation, self.lbl_evs([None]*3))
        self.assertEqual(len(c.questions), 3)
        c = ActiveLearningCore(self.relation, self.lbl_evs([False, True, None]))
        self.assertEqual(len(c.questions), 1)
        c = ActiveLearningCore(self.relation, self.lbl_evs([None, True, None]))
        self.assertEqual(len(c.questions), 2)

    def test_every_question_answered_is_not_a_question_any_more(self):
        c = ActiveLearningCore(self.relation, self.lbl_evs([None]*3))
        c.add_answer(self.ev1, False)
        self.assertEqual(len(c.questions), 2)
        self.assertNotIn(self.ev1, c.questions)


class TestProcess(ActiveLearningTestMixin, ManagerTestCase):

    def setUp(self):
        super().setUp()
        self.c = ActiveLearningCore(self.relation, self.lbl_evs([None]*3))
        patcher = mock.patch.object(self.c, 'train_relation_classifier')
        self.mock_train_classifier = patcher.start()
        self.addCleanup(patcher.stop)

    def test_process_with_no_available_labels_does_nothing(self):
        self.c.process()
        self.assertFalse(self.mock_train_classifier.called)

    def test_process_with_not_both_labels_does_nothing(self):
        # by "both", we mean True and False
        self.c.add_answer(self.ev1, True)
        self.c.process()
        self.assertFalse(self.mock_train_classifier.called)
        self.c.add_answer(self.ev2, True)
        self.c.process()
        self.assertFalse(self.mock_train_classifier.called)
        self.c.add_answer(self.ev3, False)
        self.c.process()
        self.assertTrue(self.mock_train_classifier.called)

    def test_more_than_binary_labels_is_raise(self):
        self.c.add_answer(self.ev1, True)
        self.c.add_answer(self.ev2, False)
        self.c.add_answer(self.ev3, False)
        self.c.labeled_evidence[self.ev3] = 'weird thing'
        self.assertRaises(ValueError, self.c.process)
        self.assertFalse(self.mock_train_classifier.called)
