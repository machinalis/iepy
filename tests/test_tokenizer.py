from unittest import TestCase

import nltk
from nltk.tokenize.punkt import PunktSentenceTokenizer
try:
    from unittest import mock
except ImportError:
    import mock

from iepy.preprocess.tokenizer import en_tokenize_and_segment, _get_tokenizer


class TestTokenization(TestCase):

    def check_expected_words_are_in_tokenization(self, text, expected_words):
        words = en_tokenize_and_segment(text)['tokens']
        for expected_word in expected_words:
            self.assertIn(expected_word, words)

    def test_point_between_words_is_captured(self):
        text = u"The dog is hungry.The cat is evil."
        expected = [u"dog", u"hungry", u"evil", u"."]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_hours_are_not_splitted(self):
        text = u"It's 3:39 am, what do you want?"
        expected = [u'3:39']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_apostrophs_its_contraction_is_not_splitted(self):
        text = u"It's 3:39 am, what do you want?"
        expected = [u"It's"]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_question_mark_is_splitted(self):
        text = u"It's 3:39 am, what do you want?"
        expected = [u"want", u"?"]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_web_address_is_not_splitted(self):
        text = u"Visit http://google.com"
        expected = [u"http://google.com"]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_complex_address_is_not_splitted(self):
        text = u"Try with ssh://tom@hawk:2020 and tell me"
        expected = [u"ssh://tom@hawk:2020"]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_Im_arent_and_dont_contraction_apostrophes_are_not_splitted(self):
        text = u"I'm ready for you all. Aren't you ready?. Don't you?"
        expected = [u"I'm", "Aren't", u"Don't"]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_hyphen_dates_arent_splitted(self):
        text = u"Back to 10-23-1984 but not to 23/10/1984"
        expected = [u'10-23-1984']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_slashed_dates_are_splitted(self):
        text = u"Back to 23/10/1984"
        expected = [u"10", u"23", u"1984"]
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_hyphened_words_are_not_splitted(self):
        text = u"User-friendliness is a must, use get_text."
        expected = [u'User-friendliness']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_underscore_words_are_not_splitted(self):
        text = u"User-friendliness is a must, use get_text."
        expected = [u'get_text']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_colon_is_splitted(self):
        text = u"read what I have to say:I like turtles."
        expected = [u'say', u':', u'I']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_possesive_apostroph_IS_splitted(self):
        text = u"John's bar is cool."
        expected = [u'John', u"'s", u'cool']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_emoticons_detection(self):
        text = u"John's bar is cool, right :) XD?"
        expected = [u':)', u'XD', u'?']
        self.check_expected_words_are_in_tokenization(text, expected)

    def test_parenthesis_are_splitted(self):
        text = u"The wolf (starved to death), killed a duck."
        expected = [u'(', u'starved', u'death', u')', u',']
        self.check_expected_words_are_in_tokenization(text, expected)


class TestTokensOffsets(TestCase):

    def test_there_is_an_offset_per_token(self):
        text = u"The wolf (starved to death), killed a duck."
        tokens = en_tokenize_and_segment(text)['tokens']
        offsets = en_tokenize_and_segment(text)['spans']
        self.assertEqual(len(tokens), len(offsets))

    def test_each_offset_its_the_exac_location_pf_the_token_in_the_text(self):
        text = (u"John's bar is cool, right :) XD? "
                u"The wolf (starved to death), killed a duck."
                )
        tokens = en_tokenize_and_segment(text)['tokens']
        offsets = en_tokenize_and_segment(text)['spans']
        for tkn, off in zip(tokens, offsets):
            self.assertEqual(text[off:len(tkn)+off], tkn)


class TestSegmentation(TestCase):
    """If N sentences are found, N+1 numbers are returned, where the (i, i+1)
    numbers represent the start and end (in tokens) of the i-th sentence.
    """

    def test_cero_is_always_included(self):
        text = "The wolf killed a duck. What a pitty"
        sents = en_tokenize_and_segment(text)['sentences']
        self.assertEqual(sents[0], 0)

    def test_cero_is_all_even_if_no_tokens(self):
        text = ""
        sents = en_tokenize_and_segment(text)['sentences']
        self.assertEqual(sents, [0])

    def test_number_of_tokens_is_always_last(self):
        text = "The wolf killed a duck. What a pitty"
        pieces = en_tokenize_and_segment(text)
        sents = pieces['sentences']
        tkns = pieces['tokens']
        self.assertEqual(sents[-1], len(tkns))

    def test_nltk_punk_sentence_tokenizer_is_used(self):
        text = "The wolf killed a duck. What a pitty"
        with mock.patch.object(PunktSentenceTokenizer, 'span_tokenize') as nltk_sent:
            nltk_sent.return_value = [(0, 5)]
            en_tokenize_and_segment(text)
            nltk_sent.assert_called_once_with(text)

    def test_sentences_with_big_text(self):
        text = (u"The Bastard Operator From Hell (BOFH), a fictional character "
                u"created by Simon Travaglia, is a rogue system administrator who "
                u"takes out his anger on users (often referred to as lusers), "
                u"colleagues, bosses, and anyone else who pesters him with their "
                u"pitiful user created \"problems\".\n"
                u"The BOFH stories were originally posted in 1992 to Usenet by "
                u"Travaglia, with some being reprinted in Datamation. They were "
                u"published weekly from 1995 to 1999 in Network Week and since 2000"
                u" they have been published most weeks in The Register. They were "
                u"also published in PC Plus magazine for a short time, and several"
                u" books of the stories have also been released.")
        tokenizer = _get_tokenizer()
        expected_sentences = [0]
        sentence_splitter = nltk.data.load("tokenizers/punkt/english.pickle")
        for i, j in sentence_splitter.span_tokenize(text):
            expected_sentences.append(len(list(tokenizer.span_tokenize(text[:j]))))
        sents = en_tokenize_and_segment(text)['sentences']
        self.assertEqual(expected_sentences, sents)
