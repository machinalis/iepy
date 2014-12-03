from .factories import SentencedIEDocFactory
from .manager_case import ManagerTestCase


class TestDocumentInvariants(ManagerTestCase):

    def test_cant_set_different_number_of_synparse_than_sentences(self):
        doc = SentencedIEDocFactory()
        sents = list(doc.get_sentences())
        fake_syn_parse_items = [
            '<fake parse tree %i>' % i for i in range(len(sents) + 1)]
        with self.assertRaises(ValueError):
            doc.set_syntactic_parsing_result(fake_syn_parse_items)
