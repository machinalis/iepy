from iepy.preprocess.ner.base import FoundEntity

from .factories import SentencedIEDocFactory, GazetteItemFactory
from .manager_case import ManagerTestCase


class TestDocumentInvariants(ManagerTestCase):

    def test_cant_set_different_number_of_synparse_than_sentences(self):
        doc = SentencedIEDocFactory()
        sents = list(doc.get_sentences())
        fake_syn_parse_items = [
            '<fake parse tree %i>' % i for i in range(len(sents) + 1)]
        with self.assertRaises(ValueError):
            doc.set_syntactic_parsing_result(fake_syn_parse_items)


class TestSetNERResults(ManagerTestCase):

    def _f_eo(self, key='something', kind_name='ABC', alias='The dog', offset=0,
              offset_end=2, from_gazette=False):
        # constructs and returns a simple FoundEntity with the args given
        return FoundEntity(key=key, kind_name=kind_name, alias=alias, offset=offset,
                           offset_end=offset_end, from_gazette=from_gazette)

    def setUp(self):
        self.doc = SentencedIEDocFactory(text="The dog is dead. Long live the dog.")

    def test_simple(self):
        f_eo = self._f_eo()
        self.doc.set_ner_result([f_eo])
        self.assertEqual(self.doc.entity_occurrences.count(), 1)
        eo = self.doc.entity_occurrences.first()
        self.assertEqual(eo.entity.key, f_eo.key)
        self.assertEqual(eo.entity.kind.name, f_eo.kind_name)
        self.assertEqual(eo.entity.gazette, None)
        self.assertEqual(eo.offset, f_eo.offset)
        self.assertEqual(eo.offset_end, f_eo.offset_end)
        self.assertEqual(eo.alias, f_eo.alias)

    def test_offsets_are_checked(self):
        f_eo = self._f_eo(offset=-1)  # negative offset
        self.assertRaises(ValueError, self.doc.set_ner_result, [f_eo])
        f_eo = self._f_eo(offset=2, offset_end=2)  # end lte start
        self.assertRaises(ValueError, self.doc.set_ner_result, [f_eo])
        f_eo = self._f_eo(offset=2, offset_end=1)  # end lte start
        self.assertRaises(ValueError, self.doc.set_ner_result, [f_eo])
        doc_tkns = len(self.doc.tokens)
        f_eo = self._f_eo(offset=doc_tkns + 1,
                          offset_end=doc_tkns + 3)  # bigger than doc tokens
        self.assertRaises(ValueError, self.doc.set_ner_result, [f_eo])

    def test_if_from_gazette_is_enabled_gazetteitem_is_set(self):
        f_eo = self._f_eo(from_gazette=True)
        gz_item = GazetteItemFactory(kind__name=f_eo.kind_name,
                                     text=f_eo.key)
        self.doc.set_ner_result([f_eo])
        eo = self.doc.entity_occurrences.first()
        self.assertEqual(eo.entity.gazette, gz_item)

    def test_sending_again_same_found_entity_is_idempotent(self):
        f_eo = self._f_eo()
        self.doc.set_ner_result([f_eo])
        self.doc.set_ner_result([f_eo])
        self.assertEqual(self.doc.entity_occurrences.count(), 1)

    def test_sending_twice_same_found_entity_doesnt_crash(self):
        f_eo = self._f_eo()
        self.doc.set_ner_result([f_eo, f_eo])
        self.assertEqual(self.doc.entity_occurrences.count(), 1)

    def test_same_different_eos_with_same_offsets_and_kind_are_not_allowed(self):
        f_eo = self._f_eo()
        f_eo_2 = self._f_eo(key=f_eo.key + ' and more')  # to be sure is another key
        self.doc.set_ner_result([f_eo, f_eo_2])
        self.assertEqual(self.doc.entity_occurrences.count(), 1)
        eo = self.doc.entity_occurrences.first()
        # the one that is saved is the first one
        self.assertEqual(eo.entity.key, f_eo.key)
