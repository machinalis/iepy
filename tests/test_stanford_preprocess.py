from unittest import TestCase, mock
from datetime import datetime

from .factories import IEDocFactory
from .manager_case import ManagerTestCase
from iepy.preprocess.stanford_preprocess import (
    get_tokens, get_token_offsets,
    get_sentence_boundaries,
    get_entity_occurrences,
    StanfordPreprocess
)


def sentence_factory(description):
    sentence = []
    for line in description.split("\n"):
        line = line.strip()
        if not line:
            continue
        token, offset, ner = line.split()
        sentence.append({"word": token, "CharacterOffsetBegin": offset, "NER": ner})
    return sentence


class TestSentenceFunctions(TestCase):
    def test_get_tokens_simple(self):
        sentence = sentence_factory("""
            friends x x
            will x x
            be x x
            friends x x
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
            x 1 x
            x 4 x
            x 8 x
            x 3 x
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
            sentence_factory("x x x\n" * 3),  # 3 words
            sentence_factory("x x x\n" * 2),  # 2 words
            sentence_factory("x x x\n" * 4),  # 4 words
        ]
        #          1st 2nd 3rd   end
        expected = [0, 3, 3 + 2, 3 + 2 + 4]
        self.assertEqual(get_sentence_boundaries(sentences), expected)

    def test_offsets_and_tokens_work_togheter(self):
        sentences = [
            sentence_factory("a x x\n" * 3),  # 3 words
            sentence_factory("b x x\n" * 2),  # 2 words
            sentence_factory("c x x\n" * 4),  # 4 words
            sentence_factory("d x x\n" * 5),  # 5 words
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
            a 0  O
            b 1  B
            c 2  O
        """)
        b = sentence_factory("""
            d 3  O
            e 4  O
            f 5  O
        """)
        c = sentence_factory("""
            g 6  D
            h 7  D
            i 8  O
            j 9  O
            k 10 H
        """)
        d = sentence_factory("""
            l 11 H
            m 12 O
            n 13 O
            o 14 L
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


class TestPreProcessCall(ManagerTestCase):
    def setUp(self):
        self.preprocess = StanfordPreprocess()

        self.document_nothing_done = IEDocFactory()
        self.document_all_done = IEDocFactory(
            tokenization_done_at=datetime.now(),
            lemmatization_done_at=datetime.now(),
            sentencer_done_at=datetime.now(),
            tagging_done_at=datetime.now(),
            ner_done_at=datetime.now(),
            segmentation_done_at=datetime.now(),
        )
        self.document_missing_lemmatization = IEDocFactory(
            tokenization_done_at=datetime.now(),
            sentencer_done_at=datetime.now(),
            tagging_done_at=datetime.now(),
            ner_done_at=datetime.now(),
            segmentation_done_at=datetime.now(),
        )

    def test_non_step_is_run(self):

        with mock.patch("iepy.preprocess.corenlp.get_analizer") as mock_analizer:
            self.preprocess(self.document_all_done)
            self.assertFalse(mock_analizer.called)

    def test_lemmatization_is_run_even_all_others_already_did(self):

        with mock.patch.object(self.preprocess, "lemmatization_only") as mock_lemmatization:
            mock_lemmatization.side_effect = lambda x: None
            self.preprocess(self.document_missing_lemmatization)
            self.assertTrue(mock_lemmatization.called)

    def test_override(self):
        self.override_preprocess = StanfordPreprocess()
        self.override_preprocess.override = True

        with mock.patch("iepy.preprocess.corenlp.get_analizer") as mock_analizer:
            class MockAnalizer:
                def analize(self, *args, **kwargs):
                    return {}

            mock_analizer.side_effect = lambda: MockAnalizer
            self.override_preprocess(self.document_all_done)
            self.assertTrue(mock_analizer.called)

    def test_all_process_called(self):
        with mock.patch("iepy.preprocess.corenlp.get_analizer") as mock_analizer:
            class MockAnalizer:
                def analize(self, *args, **kwargs):
                    return {}

            mock_analizer.side_effect = lambda: MockAnalizer
            self.preprocess(self.document_nothing_done)

        self.assertNotEqual(self.document_nothing_done.tokenization_done_at, None)
        self.assertNotEqual(self.document_nothing_done.lemmatization_done_at, None)
        self.assertNotEqual(self.document_nothing_done.tagging_done_at, None)
        self.assertNotEqual(self.document_nothing_done.ner_done_at, None)
        self.assertNotEqual(self.document_nothing_done.sentencer_done_at, None)
