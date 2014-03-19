from unittest import TestCase

from iepy.lit_tagger import LitTagger


class TestLitTagger(TestCase):

    def test_stanford_style(self):
        tmp_filename = 'tmp_test_lit_tagger.txt'
        f = open(tmp_filename, 'w')
        f.write('HIV\nHepatitis C\nMRI\nCT scan\nbrain tumor\n')
        f.close()
        
        tagger = LitTagger('MEDIC_STUFF', tmp_filename)
        
        s = "Chase notes she's negative for HIV and Hepatitis C"
        result = tagger.tag(s.split())
        tags = [tag for _, tag in result]
        expected_tags = ['O', 'O', 'O', 'O', 'O', 'MEDIC_STUFF', 'O', 
                                                'MEDIC_STUFF', 'MEDIC_STUFF']
        self.assertEqual(tags, expected_tags)

    def test_offset_style(self):
        tmp_filename = 'tmp_test_lit_tagger.txt'
        f = open(tmp_filename, 'w')
        f.write('HIV\nHepatitis C\nMRI\nCT scan\nbrain tumor\n')
        f.close()
        
        tagger = LitTagger('MEDIC_STUFF', tmp_filename)
        
        s = "Chase notes she's negative for HIV and Hepatitis C"
        result = tagger.entities(s.split())
        expected_entities = [(5, 6), (7, 9)]
        
        self.assertEqual(result, expected_entities)

