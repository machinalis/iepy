from unittest import TestCase

from iepy.lit_tagger import LitTagger, LitTaggerRunner
from iepy.models import PreProcessSteps, IEDocument
from tests.factories import SentencedIEDocFactory
from tests.manager_case import ManagerTestCase


class TestLitTagger(TestCase):

    def test_tagging(self):
        tmp_filename1 = 'tmp_test_lit_tagger_disease.txt'
        f = open(tmp_filename1, 'w')
        f.write('HIV\nHepatitis C\nbrain tumor\n')
        f.close()
        tmp_filename2 = 'tmp_test_lit_tagger_medical_test.txt'
        f = open(tmp_filename2, 'w')
        f.write('MRI\nCT scan\n')
        f.close()
        
        tagger = LitTagger(['DISEASE', 'MEDICAL_TEST'], 
                            [tmp_filename1, tmp_filename2])
        
        s = "Chase notes she's negative for HIV and Hepatitis C"
        result = tagger.tag(s.split())
        tags = [tag for _, tag in result]
        expected_tags = 'O O O O O DISEASE O DISEASE DISEASE'.split()
        self.assertEqual(tags, expected_tags)

        s = "Cuddy points out that the CT scan showed the patient has a metal pin in her arm and can't undergo an MRI"
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
        tmp_filename1 = 'tmp_test_lit_tagger_disease.txt'
        f = open(tmp_filename1, 'w')
        f.write('HIV\nHepatitis C\nbrain tumor\n')
        f.close()
        tmp_filename2 = 'tmp_test_lit_tagger_medical_test.txt'
        f = open(tmp_filename2, 'w')
        f.write('MRI\nCT scan\n')
        f.close()
        
        tagger = LitTagger(['DISEASE', 'MEDICAL_TEST'], 
                            [tmp_filename1, tmp_filename2])
        
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


class TestLitTaggerRunner(ManagerTestCase):

    ManagerClass = IEDocument

    def test(self):
        doc = SentencedIEDocFactory(
                    text="Chase notes she's negative for HIV and Hepatitis C")
        tmp_filename = 'tmp_test_lit_tagger.txt'
        f = open(tmp_filename, 'w')
        f.write('HIV\nHepatitis C\nMRI\nCT scan\nbrain tumor\n')
        f.close()
        
        lit_tagger_runner = LitTaggerRunner(['DISEASE'], [tmp_filename])
        lit_tagger_runner(doc)
        
        # (the tokenizer splits she's in two parts)
        entities_triples = [(6, 7, 'disease'), (8, 10, 'disease')]
        
        self.assertTrue(doc.was_preprocess_done(PreProcessSteps.nerc))
        entities = doc.get_preprocess_result(PreProcessSteps.nerc)
        
        self.assertEqual(len(entities), len(entities_triples))
        for e, (offset, offset_end, kind) in zip(entities, entities_triples):
            self.assertEqual(e.offset, offset)
            self.assertEqual(e.offset_end, offset_end)
            self.assertEqual(e.entity.kind, kind)

