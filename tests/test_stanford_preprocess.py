from unittest import TestCase, mock
from datetime import datetime

from .factories import IEDocFactory, SentencedIEDocFactory, GazetteItemFactory
from .manager_case import ManagerTestCase
from iepy.preprocess.stanford_preprocess import (
    get_tokens, get_token_offsets, get_lemmas,
    get_sentence_boundaries,
    get_entity_occurrences,
    StanfordPreprocess,
    generate_gazettes_file, GAZETTE_PREFIX, get_found_entities,
    unescape_gazette, escape_gazette,
)


def sentence_factory(description):
    sentence = []
    for line in description.split("\n"):
        line = line.strip()
        if not line:
            continue
        token, offset, ner, lemma = line.split()
        sentence.append({
            "word": token,
            "CharacterOffsetBegin": offset,
            "NER": ner,
            "lemma": lemma,
        })
    return sentence


class TestSentenceFunctions(TestCase):
    def test_get_tokens_simple(self):
        sentence = sentence_factory("""
            friends x x x
            will x x x
            be x x x
            friends x x x
        """)
        X = get_tokens([sentence])
        self.assertEqual(X, "friends will be friends".split())

    def test_get_tokens_empty(self):
        self.assertEqual(get_tokens([]), [])

    def test_get_tokens_invalid_data(self):
        with self.assertRaises(KeyError):
            get_tokens([[{"aaa": "bbb"}]])

    def test_get_token_offsets_simple(self):
        sentence = sentence_factory("""
            x 1 x x
            x 4 x x
            x 8 x x
            x 3 x x
        """)
        X = get_token_offsets([sentence])
        self.assertEqual(X, [1, 4, 8, 3])

    def test_get_token_offsets_empty(self):
        self.assertEqual(get_token_offsets([]), [])

    def test_get_token_offsets_invalid_data(self):
        with self.assertRaises(KeyError):
            get_token_offsets([[{"aaa": "bbb"}]])

    def test_sentence_boundaries_empty(self):
        self.assertEqual(get_sentence_boundaries([]), [0])

    def test_sentence_boundaries_simple(self):
        sentences = [
            sentence_factory("x x x x\n" * 3),  # 3 words
            sentence_factory("x x x x\n" * 2),  # 2 words
            sentence_factory("x x x x\n" * 4),  # 4 words
        ]
        #          1st 2nd 3rd   end
        expected = [0, 3, 3 + 2, 3 + 2 + 4]
        self.assertEqual(get_sentence_boundaries(sentences), expected)

    def test_offsets_and_tokens_work_togheter(self):
        sentences = [
            sentence_factory("a x x x\n" * 3),  # 3 words
            sentence_factory("b x x x\n" * 2),  # 2 words
            sentence_factory("c x x x\n" * 4),  # 4 words
            sentence_factory("d x x x\n" * 5),  # 5 words
        ]
        words = get_tokens(sentences)
        offsets = get_sentence_boundaries(sentences)
        self.assertEqual(len(words), offsets[-1])
        self.assertEqual(words[offsets[1]], "b")
        self.assertEqual(words[offsets[1] - 1], "a")
        self.assertEqual(words[offsets[3]], "d")
        self.assertEqual(words[offsets[3] - 1], "c")

    def test_get_entity_occurrences_simple(self):
        a = sentence_factory("""
            a 0  O x
            b 1  B x
            c 2  O x
        """)
        b = sentence_factory("""
            d 3  O x
            e 4  O x
            f 5  O x
        """)
        c = sentence_factory("""
            g 6  D x
            h 7  D x
            i 8  O x
            j 9  O x
            k 10 H x
        """)
        d = sentence_factory("""
            l 11 H x
            m 12 O x
            n 13 O x
            o 14 L x
        """)
        sentences = [a, b, c, d]
        expected = [
            (1, 2, "B"),  # this is the b letter in the first sentence
            (6, 8, "D"),  # first two words of the third sentence
            (10, 11, "H"),  # last word of the third sentence
            (11, 12, "H"),  # first word of the fourth sentence
            (14, 15, "L"),  # last word of the fourth sentence
        ]
        self.assertEqual(get_entity_occurrences(sentences), expected)

    def test_get_lemmas_empty(self):
        self.assertEqual(get_lemmas([]), [])

    def test_get_lemmas_and_tokens_same_length(self):
        sentences = [
            sentence_factory("x x x x\n" * 3),  # 3 words
            sentence_factory("x x x x\n" * 2),  # 2 words
            sentence_factory("x x x x\n" * 4),  # 4 words
            sentence_factory("x x x x\n" * 5),  # 5 words
        ]
        tokens = get_tokens(sentences)
        lemmas = get_lemmas(sentences)
        self.assertEqual(len(tokens), len(lemmas))


class TestPreProcessCall(ManagerTestCase):

    def _doc_creator(self, steps):
        doc = SentencedIEDocFactory()
        for step in steps.split():
            if step:
                setattr(doc, "{}_done_at".format(step), datetime.now())
        doc.save()
        return doc

    def setUp(self):

        self.document_nothing_done = IEDocFactory()
        self.document_all_done = self._doc_creator("tokenization lemmatization sentencer tagging ner segmentation syntactic_parsing")
        self.document_missing_lemmatization = self._doc_creator("tokenization sentencer tagging ner segmentation syntactic_parsing")
        self.document_missing_syntactic_parsing = self._doc_creator("tokenization sentencer tagging ner segmentation lemmatization")

    def test_non_step_is_run(self):
        with mock.patch("iepy.preprocess.corenlp.get_analizer"):
            preprocess = StanfordPreprocess()
            with mock.patch.object(preprocess.corenlp, "analize") as mock_analize:
                preprocess(self.document_all_done)
                self.assertFalse(mock_analize.called)

    def test_lemmatization_is_run_even_all_others_already_did(self):

        with mock.patch("iepy.preprocess.corenlp.get_analizer"):
            preprocess = StanfordPreprocess()
            with mock.patch.object(preprocess, "lemmatization_only") as mock_lemmatization:
                mock_lemmatization.side_effect = lambda x: None
                preprocess(self.document_missing_lemmatization)
                self.assertTrue(mock_lemmatization.called)

    def test_override(self):
        with mock.patch("iepy.preprocess.corenlp.get_analizer") as mock_analizer:
            class MockAnalizer:
                def analize(self, *args, **kwargs):
                    return {}
            mock_analizer.return_value = MockAnalizer()

            self.override_preprocess = StanfordPreprocess()
            self.override_preprocess.override = True
            self.override_preprocess(self.document_all_done)
            self.assertTrue(mock_analizer.called)

    def test_all_process_called(self):
        with mock.patch("iepy.preprocess.corenlp.get_analizer") as mock_analizer:
            class MockAnalizer:
                def analize(self, *args, **kwargs):
                    return {}
            mock_analizer.return_value = MockAnalizer()

            preprocess = StanfordPreprocess()
            preprocess(self.document_nothing_done)

        self.assertNotEqual(self.document_nothing_done.tokenization_done_at, None)
        self.assertNotEqual(self.document_nothing_done.lemmatization_done_at, None)
        self.assertNotEqual(self.document_nothing_done.tagging_done_at, None)
        self.assertNotEqual(self.document_nothing_done.ner_done_at, None)
        self.assertNotEqual(self.document_nothing_done.sentencer_done_at, None)

    def test_syntactic_parsing_is_run_even_all_others_already_did(self):
        with mock.patch("iepy.preprocess.corenlp.get_analizer"):
            preprocess = StanfordPreprocess()
            with mock.patch.object(preprocess, "syntactic_parsing_only") as mock_lemmatization:
                mock_lemmatization.side_effect = lambda x: None
                preprocess(self.document_missing_syntactic_parsing)
                self.assertTrue(mock_lemmatization.called)

    def test_syntactic_parsing_invalid_trees(self):
        with mock.patch("iepy.preprocess.corenlp.get_analizer"):
            preprocess = StanfordPreprocess()
            with mock.patch("iepy.preprocess.stanford_preprocess.analysis_to_parse_trees") as mock_analysis:
                sentences = list(self.document_missing_syntactic_parsing.get_sentences())
                mock_analysis.side_effect = ["x"] * int(len(sentences) / 2)
                with self.assertRaises(ValueError):
                    preprocess(self.document_missing_syntactic_parsing)


class TestGazetteer(ManagerTestCase):
    def test_generate_gazettes_file_emtpy(self):
        self.assertEqual(generate_gazettes_file(), None)

    def _test_single_gazette(self, text=None):
        if text:
            gazette_item = GazetteItemFactory(text=text)
        else:
            gazette_item = GazetteItemFactory()
        filepath = generate_gazettes_file()
        self.assertNotEqual(filepath, None)
        data = open(filepath).read()

        data = data.split("\n")
        self.assertEqual(len(data), 2)
        data = data[0].split("\t")
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0], escape_gazette(gazette_item.text))
        self.assertEqual(data[1], "{}{}".format(GAZETTE_PREFIX, gazette_item.kind.name))
        gazette_item.delete()

    def test_generate_gazettes_several_lines(self):
        gazettes = [GazetteItemFactory() for x in range(10)]
        filepath = generate_gazettes_file()
        self.assertNotEqual(filepath, None)
        data = open(filepath).read()
        self.assertEqual(data.count("\n"), 10)
        for line in data.split("\n")[:-1]:
            self.assertEqual(line.count("\t"), 2)

    def test_generate_gazettes_one_line(self):
        self._test_single_gazette()

    def test_gazettes_unicode(self):
        self._test_single_gazette("#½]}→@}#½ĸ@#")
        self._test_single_gazette("ħøłæ")
        self._test_single_gazette("æ}@ł¢µ«»µ«»“~þðøđþ")
        self._test_single_gazette("\ || \ ()(()))) \\ |")

    def test_gazettes_different_eo_has_different_entity(self):
        document = IEDocFactory()
        tokens = "Hugh Laurie stars in Stuart Little with Michael J. Fox, the one from Back to The Future".split()
        sentences = [
            sentence_factory(" ".join(["{} x x x\n".format(x) for x in tokens])),
        ]
        with mock.patch("iepy.preprocess.stanford_preprocess.get_entity_occurrences") as mock_eos:
            mock_eos.return_value = [
                (0, 2, "person"),
                (4, 6, "{}MOVIE".format(GAZETTE_PREFIX)),
                (7, 10, "person"),
                (13, 17, "{}MOVIE".format(GAZETTE_PREFIX)),
            ]

            found_entities = get_found_entities(document, sentences, tokens)
            self.assertEqual(len(found_entities), 4)
            gazettes = [x for x in found_entities if x.from_gazette]
            self.assertEqual(len(gazettes), 2)
            self.assertNotEqual(gazettes[0].key, gazettes[1].key)

    def test_gazettes_same_eo_has_same_entity(self):
        document = IEDocFactory()
        tokens = "Hugh Laurie stars in Stuart Little. Michael J. Fox also works in Stuart Little.".split()
        sentences = [
            sentence_factory(" ".join(["{} x x x\n".format(x) for x in tokens])),
        ]
        with mock.patch("iepy.preprocess.stanford_preprocess.get_entity_occurrences") as mock_eos:
            mock_eos.return_value = [
                (0, 2, "person"),
                (4, 6, "{}MOVIE".format(GAZETTE_PREFIX)),
                (6, 9, "person"),
                (12, 14, "{}MOVIE".format(GAZETTE_PREFIX)),
            ]

            found_entities = get_found_entities(document, sentences, tokens)
            self.assertEqual(len(found_entities), 4)
            gazettes = [x for x in found_entities if x.from_gazette]
            self.assertEqual(len(gazettes), 2)
            self.assertEqual(gazettes[0].key, gazettes[1].key)

    def test_escaping(self):
        text_and_expected = (
            ("Maradona", "Maradona"),
            ("El Diego", "El Diego"),
            ("El Diego ( el 10 )", "El Diego \( el 10 \)"),
            ("|()|", "\|\(\)\|"),
            ("æßðæßð", "æßðæßð"),
            ("\ hello \ ", "\\\\ hello \\\\ "),
            ("*", "\*"),
        )

        for text, expected in text_and_expected:
            self.assertEqual(escape_gazette(text), expected)

    def test_escaping_unescape(self):
        texts = ["Maradona", "El Diego", "El Diego ( el 10 )", "|()|", "æßðæßð", "\ hello \ "]
        for text in texts:
            self.assertEqual(unescape_gazette(escape_gazette(text)), text)
