from unittest import TestCase

from iepy.data.models import IEDocument
from iepy.preprocess.ner.literal import LiteralNER, LiteralNERRunner
from iepy.preprocess.pipeline import PreProcessSteps
from tests.factories import SentencedIEDocFactory, NamedTemporaryFile23
from tests.manager_case import ManagerTestCase
from tests.test_ner import NERTestMixin

NEW_ENTITIES = ['DISEASE', 'MEDICAL_TEST']


class TestLiteralNER(TestCase):

    def setUp(self):
        f = NamedTemporaryFile23(mode="w", encoding="utf8")
        f.write('HIV\nHepatitis C\nbrain tumor\ndrooling\n')
        f.seek(0)
        self.tmp_file1 = f
        f = NamedTemporaryFile23(mode="w", encoding="utf8")
        f.write('MRI\nCT scan\ndrooling\n')
        f.seek(0)
        self.tmp_file2 = f

    def test_tagging(self):
        tagger = LiteralNER(NEW_ENTITIES,
                            [self.tmp_file1.name, self.tmp_file2.name])

        s = "Chase notes she's negative for HIV and Hepatitis C"
        result = tagger.tag(s.split())
        tags = [tag for _, tag in result]
        expected_tags = 'O O O O O DISEASE O DISEASE DISEASE'.split()
        self.assertEqual(tags, expected_tags)

        s = ("Cuddy points out that the CT scan showed the patient has a metal "
             "pin in her arm and can't undergo an MRI")
        result = tagger.tag(s.split())
        tags = [tag for _, tag in result]
        expected_tags = 'O O O O O MEDICAL_TEST MEDICAL_TEST O O O O O O O O O O O O O O MEDICAL_TEST'.split()
        self.assertEqual(tags, expected_tags)

        s = "CT scan said HIV MRI Hepatitis C"
        result = tagger.tag(s.split())
        tags = [tag for _, tag in result]
        expected_tags = 'MEDICAL_TEST MEDICAL_TEST O DISEASE MEDICAL_TEST DISEASE DISEASE'.split()
        self.assertEqual(tags, expected_tags)

    def test_entities(self):
        tagger = LiteralNER(NEW_ENTITIES,
                            [self.tmp_file1.name, self.tmp_file2.name])

        s = "Chase notes she's negative for HIV and Hepatitis C"
        result = tagger.entities(s.split())
        expected_entities = [((5, 6), 'DISEASE'), ((7, 9), 'DISEASE')]
        self.assertEqual(result, expected_entities)

        s = "Cuddy points out that the CT scan showed the patient has a metal pin in her arm and can't undergo an MRI"
        result = tagger.entities(s.split())
        expected_entities = [((5, 7), 'MEDICAL_TEST'), ((21, 22), 'MEDICAL_TEST')]
        self.assertEqual(result, expected_entities)

        s = "CT scan said HIV MRI Hepatitis C"
        result = tagger.entities(s.split())
        expected_entities = [((0, 2), 'MEDICAL_TEST'), ((3, 4), 'DISEASE'),
                             ((4, 5), 'MEDICAL_TEST'), ((5, 7), 'DISEASE')]
        self.assertEqual(result, expected_entities)


class TestLiteralNERRunner(ManagerTestCase, NERTestMixin):

    def setUp(self):
        f = NamedTemporaryFile23(mode="w", encoding="utf8")
        f.write('HIV\nHepatitis C\nbrain tumor\ndrooling\n')
        f.seek(0)
        self.tmp_file1 = f
        f = NamedTemporaryFile23(mode="w", encoding="utf8")
        f.write('MRI\nCT scan\ndrooling\n')
        f.seek(0)
        self.tmp_file2 = f

    def test(self):
        doc = SentencedIEDocFactory(
            text="Chase notes she's negative for HIV and Hepatitis C")

        lit_tagger_runner = LiteralNERRunner(['disease'], [self.tmp_file1.name])
        lit_tagger_runner(doc)

        # (the tokenizer splits she's in two parts)
        entities_triples = [(6, 7, 'disease'), (8, 10, 'disease')]

        self.check_ner_result(doc, entities_triples)
