from iepy.preprocess.ner.regexp import RegExpNERRunner

from .factories import SentencedIEDocFactory
from .manager_case import ManagerTestCase
from .test_ner import NERTestMixin


class TestRegExpNERRunner(ManagerTestCase, NERTestMixin):

    def test(self):
        doc = SentencedIEDocFactory(
            text="Chase notes she's negative for HIV and Hepatitis C")
        ner_runner = RegExpNERRunner('disease', '<HIV>|<Hepatitis><[A-C]>')
        ner_runner(doc)
        # (the tokenizer splits she's in two parts)
        entities_triples = [(6, 7, 'DISEASE'), (8, 10, 'DISEASE')]
        self.check_ner_result(doc, entities_triples)

        doc = SentencedIEDocFactory(
            text="Cuddy points out that the CT scan showed the patient has a metal pin in her arm and can't undergo an MRI")
        ner_runner = RegExpNERRunner('MEDICAL_TEST', '<[A-Z]+><scan>|<MRI>')
        ner_runner(doc)
        # (the tokenizer splits can't in two parts)
        entities_triples = [(5, 7, 'MEDICAL_TEST'), (22, 23, 'MEDICAL_TEST')]
        self.check_ner_result(doc, entities_triples)
