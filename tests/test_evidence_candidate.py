from .manager_case import ManagerTestCase
from iepy.data.models import EvidenceLabel
from .factories import (
    EntityFactory, EntityKindFactory,
    RelationFactory, EvidenceCandidateFactory
)

class TestEvidenceCandidate(ManagerTestCase):
    judge = "iepy"

    def setUp(self):
        self.k_person = EntityKindFactory(name='person')
        self.k_location = EntityKindFactory(name='location')
        self.e_john = EntityFactory(key='john', kind=self.k_person)
        self.e_bob = EntityFactory(key='bob', kind=self.k_person)
        self.e_argentina = EntityFactory(key='argentina', kind=self.k_location)
        self.e_germany = EntityFactory(key='germany', kind=self.k_location)
        self.e_australia = EntityFactory(key='australia', kind=self.k_location)
        self.person_location_relation = RelationFactory(
            left_entity_kind=self.k_person,
            right_entity_kind=self.k_location
        )
        self.positive_label = EvidenceLabel.YESRELATION
        self.negative_label = EvidenceLabel.NORELATION

    def test_save_label(self):
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 0)
        candidate = EvidenceCandidateFactory()
        candidate.set_label(self.positive_label, self.judge)
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertEqual(label.label, self.positive_label)
        self.assertEqual(label.judge, self.judge)
        self.assertEqual(label.evidence_candidate, candidate)

    def test_save_label_twice(self):
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 0)
        candidate = EvidenceCandidateFactory()
        candidate.set_label(self.positive_label, self.judge)
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 1)
        candidate.set_label(self.negative_label, self.judge)
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 1)
        label = labels[0]
        self.assertEqual(label.label, self.negative_label)
        self.assertEqual(label.judge, self.judge)
        self.assertEqual(label.evidence_candidate, candidate)

    def test_save_diferent_judges(self):
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 0)
        candidate = EvidenceCandidateFactory()
        candidate.set_label(self.positive_label, "judge1")
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 1)
        candidate.set_label(self.negative_label, "judge2")
        labels = list(EvidenceLabel.objects.all())
        self.assertEqual(len(labels), 2)

        label1, label2 = labels
        self.assertNotEqual(label1.judge, label2.judge)
        self.assertNotEqual(label1.label, label2.label)
