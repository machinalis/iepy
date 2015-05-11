from unittest import TestCase, mock
from datetime import datetime

from .factories import (IEDocFactory, SentencedIEDocFactory, GazetteItemFactory,
                        EntityOccurrenceFactory, EntityKindFactory)
from .manager_case import ManagerTestCase
from iepy.preprocess.pipeline import PreProcessSteps
from iepy.preprocess.stanford_preprocess import (
    StanfordPreprocess, GazetteManager, apply_coreferences, CoreferenceError,
    StanfordAnalysis)


class TestableStanfordAnalysis(StanfordAnalysis):

    def __init__(self, hacked_sentences, *args):
        self.hacked_sentences = hacked_sentences
        super().__init__({})

    def get_sentences(self):
        return self.hacked_sentences


def sentence_factory(markup):
    """Simplistic builder of *parsed* sentences.
    Each line in the markup is interpreted as a whitespace-separated-values for
        token offset-in-chars ner lemma
    which are returned as a list of dicts.
    """
    sentence = []
    for line in markup.split("\n"):
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


def get_analysis_from_sent_markup(markup):
    sentences = [sentence_factory(markup)]
    return TestableStanfordAnalysis(hacked_sentences=sentences)


class TestSentenceFunctions(TestCase):
    def test_get_tokens_simple(self):
        analysis = get_analysis_from_sent_markup("""
            friends x x x
            will x x x
            be x x x
            friends x x x
        """)
        X = analysis.get_tokens()
        self.assertEqual(X, "friends will be friends".split())

    def test_get_tokens_empty(self):
        self.assertEqual(TestableStanfordAnalysis([]).get_tokens(),
                         [])

    def test_get_tokens_invalid_data(self):
        with self.assertRaises(KeyError):
            TestableStanfordAnalysis([[{"aaa": "bbb"}]]).get_tokens()

    def test_get_token_offsets_simple(self):
        analysis = get_analysis_from_sent_markup("""
            x 1 x x
            x 4 x x
            x 8 x x
            x 3 x x
        """)
        X = analysis.get_token_offsets()
        self.assertEqual(X, [1, 4, 8, 3])

    def test_get_token_offsets_empty(self):
        self.assertEqual(TestableStanfordAnalysis([]).get_token_offsets(), [])

    def test_get_token_offsets_invalid_data(self):
        with self.assertRaises(KeyError):
            TestableStanfordAnalysis([[{"aaa": "bbb"}]]).get_token_offsets()

    def test_sentence_boundaries_empty(self):
        self.assertEqual(TestableStanfordAnalysis([]).get_sentence_boundaries(), [0])

    def test_sentence_boundaries_simple(self):
        sentences = [
            sentence_factory("x x x x\n" * 3),  # 3 words
            sentence_factory("x x x x\n" * 2),  # 2 words
            sentence_factory("x x x x\n" * 4),  # 4 words
        ]
        #          1st 2nd 3rd   end
        expected = [0, 3, 3 + 2, 3 + 2 + 4]
        analysis = TestableStanfordAnalysis(sentences)
        self.assertEqual(analysis.get_sentence_boundaries(), expected)

    def test_offsets_and_tokens_work_togheter(self):
        sentences = [
            sentence_factory("a x x x\n" * 3),  # 3 words
            sentence_factory("b x x x\n" * 2),  # 2 words
            sentence_factory("c x x x\n" * 4),  # 4 words
            sentence_factory("d x x x\n" * 5),  # 5 words
        ]
        analysis = TestableStanfordAnalysis(sentences)
        words = analysis.get_tokens()
        offsets = analysis.get_sentence_boundaries()
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
        analysis = TestableStanfordAnalysis([a, b, c, d])
        expected = [
            (1, 2, "B"),  # this is the b letter in the first sentence
            (6, 8, "D"),  # first two words of the third sentence
            (10, 11, "H"),  # last word of the third sentence
            (11, 12, "H"),  # first word of the fourth sentence
            (14, 15, "L"),  # last word of the fourth sentence
        ]
        self.assertEqual(analysis.get_entity_occurrences(), expected)

    def test_get_lemmas_empty(self):
        self.assertEqual(TestableStanfordAnalysis([]).get_lemmas(), [])

    def test_get_lemmas_and_tokens_same_length(self):
        sentences = [
            sentence_factory("x x x x\n" * 3),  # 3 words
            sentence_factory("x x x x\n" * 2),  # 2 words
            sentence_factory("x x x x\n" * 4),  # 4 words
            sentence_factory("x x x x\n" * 5),  # 5 words
        ]
        analysis = TestableStanfordAnalysis(sentences)
        tokens = analysis.get_tokens()
        lemmas = analysis.get_lemmas()
        self.assertEqual(len(tokens), len(lemmas))


class TestPreProcessCall(ManagerTestCase):

    def _doc_creator(self, mark_as_done):
        doc = SentencedIEDocFactory()
        for step in mark_as_done:
            setattr(doc, "{}_done_at".format(step.name), datetime.now())
        doc.save()
        return doc

    def setUp(self):
        pps = PreProcessSteps
        self._all_steps = [
            pps.tokenization,
            pps.sentencer,
            pps.tagging,
            pps.ner,
            pps.lemmatization,
            pps.syntactic_parsing
        ]

        patcher = mock.patch("iepy.preprocess.corenlp.get_analizer")
        self.mock_get_analizer = patcher.start()
        self.mock_analizer = self.mock_get_analizer.return_value
        self.addCleanup(patcher.stop)
        self.stanfordpp = StanfordPreprocess()

    def test_if_all_steps_are_done_then_no_step_is_run(self):
        doc = self._doc_creator(mark_as_done=self._all_steps)
        self.stanfordpp(doc)
        self.assertFalse(self.mock_analizer.analyse.called)

    def test_if_all_steps_are_done_but_in_override_mode_then_all_are_run_again(self):
        doc = self._doc_creator(mark_as_done=self._all_steps[:])
        self.mock_analizer.analyse.return_value = {}
        self.stanfordpp.override = True
        self.stanfordpp(doc)
        self.assertTrue(self.mock_analizer.analyse.called)

    def test_for_new_doc_all_steps_are_done_when_preprocessed(self):
        doc = IEDocFactory()
        self.mock_analizer.analyse.return_value = {}
        self.stanfordpp(doc)
        for step in self._all_steps:
            self.assertTrue(doc.was_preprocess_step_done(step))

    def test_lemmatization_is_run_even_all_others_already_did(self):
        # On release 0.9.1 lemmatization was added. This checks it's possible to
        # increment older preprocessed docs
        doc_no_lemmas = self._doc_creator(
            [s for s in self._all_steps if s is not PreProcessSteps.lemmatization])
        with mock.patch.object(self.stanfordpp, "lemmatization_only") as mock_lemmatization:
            mock_lemmatization.side_effect = lambda x: None
            self.stanfordpp(doc_no_lemmas)
            self.assertTrue(mock_lemmatization.called)

    def test_syntactic_parsing_is_run_even_all_others_already_did(self):
        # On release 0.9.2 syntac parsing was added. This checks it's possible to
        # increment older preprocessed docs
        doc_no_synparse = self._doc_creator(
            [s for s in self._all_steps if s is not PreProcessSteps.syntactic_parsing])
        with mock.patch.object(self.stanfordpp, "syntactic_parsing_only") as mock_synparse:
            mock_synparse.side_effect = lambda x: None
            self.stanfordpp(doc_no_synparse)
            self.assertTrue(mock_synparse.called)

    def test_can_add_ner_on_incremental_mode_over_already_preprocessed_documents(self):
        doc_done = self._doc_creator(mark_as_done=self._all_steps)
        doc_fresh = IEDocFactory()
        self.stanfordpp.increment_ner = True
        p = lambda x: mock.patch.object(self.stanfordpp, x)
        with p("increment_ner_only") as mock_ner_only:
            with p("run_everything") as mock_run_everything:
                self.stanfordpp(doc_done)
                self.assertEqual(mock_ner_only.call_count, 1)
                self.assertEqual(mock_run_everything.call_count, 0)
                self.stanfordpp(doc_fresh)
                self.assertEqual(mock_ner_only.call_count, 1)
                self.assertEqual(mock_run_everything.call_count, 1)


class TestGazetteer(ManagerTestCase):

    def test_generate_gazettes_file_empty(self):
        self.assertEqual(GazetteManager().generate_stanford_gazettes_file(), None)

    def _test_single_gazette(self, text=None):
        if text:
            gazette_item = GazetteItemFactory(text=text)
        else:
            gazette_item = GazetteItemFactory()
        gzmanager = GazetteManager()
        filepath = gzmanager.generate_stanford_gazettes_file()
        self.assertNotEqual(filepath, None)
        data = open(filepath).read().split("\n")
        self.assertEqual(len(data), 2)
        data = data[0].split("\t")
        self.assertEqual(len(data), 3)

        self.assertEqual(data[0], gzmanager.escape_text(gazette_item.text))
        self.assertEqual(data[1], "{}{}".format(gzmanager._PREFIX, gazette_item.kind.name))
        gazette_item.delete()

    def test_generate_gazettes_several_lines(self):
        [GazetteItemFactory() for x in range(10)]
        filepath = GazetteManager().generate_stanford_gazettes_file()
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

    def test_gazettes_same_eo_has_same_entity(self):
        tokens = "The nominates were Stuart Little and Memento but the winner was Stuart Little".split()
        analysis = get_analysis_from_sent_markup(
            " ".join(["{} x x x\n".format(x) for x in tokens]))

        fake_gazetter = mock.MagicMock()
        fake_gazetter.was_entry_created_by_gazette.return_value = True

        with mock.patch.object(analysis, "get_entity_occurrences") as mock_eos:
            mock_eos.return_value = [
                (3, 5, "MOVIE"),  # first occurrence of "Stuart Little"
                (6, 7, "MOVIE"),  # occurrence of "Memento"
                (11, 13, "MOVIE"),  # second occurrence of "Stuart Little"
            ]

            found_entities = analysis.get_found_entities('random_string', fake_gazetter)
            # Ok, so, Occurrences with same alias, if came from gazetter, are same Entity
            self.assertEqual(found_entities[0].key, found_entities[2].key)
            # But ofcourse, if have different aliases, not
            self.assertNotEqual(found_entities[0].key, found_entities[1].key)

    def test_escaping(self):
        texts = [
            "Maradona",
            "El Diego",
            "El Diego ( el 10 )",
            "|()|",
            "æßðæßð",
            "\ hello \ ",
            "*",
        ]
        gm = GazetteManager()
        for text in texts:
            escaped = gm.escape_text(text)
            self.assertEqual(escaped.count("\Q"), len(text.split()))
            self.assertEqual(escaped.count("\E"), len(text.split()))


class TestMergeCorreferences(ManagerTestCase):

    def setUp(self):
        self.doc = SentencedIEDocFactory(
            text="Diego did it . He scored on the first half , and now he did it again . "
                 #0     1   2  3 4  5      6  7   8     9   10 11  12  13 14  15 16    17
                 "Diego Maradona , the best player ever , won the game alone .")
                 #18    19      20 21  22   23     24  25 26  27  28   29    30
        # mentions is a list of triplets (start, end, head) of each mention
        self.mentions = [(0, 1, 0),  # Diego
                         (4, 5, 4),  # He
                         (13, 14, 13),  # he
                         (18, 20, 18),  # Diego Maradona
                         (21, 25, 23),  # the best player ever
                         ]
        assert self.doc.entity_occurrences.count() == 0
        self.sample_ekind = EntityKindFactory()

    def merge(self, correfs):
        # runs the method on document
        return apply_coreferences(self.doc, correfs)

    def create_eo_with_mention(self, mention):
        return EntityOccurrenceFactory(
            document=self.doc, entity__kind=self.sample_ekind,
            offset=mention[0], offset_end=mention[1])

    def test_if_none_of_the_mentions_is_already_and_EO_nothing_happens(self):
        self.merge(self.mentions[:])
        self.assertEqual(self.doc.entity_occurrences.count(), 0)

    def test_merging_when_there_are_EOS_from_different_kind_fails(self):
        for m in self.mentions[:2]:
            eo = self.create_eo_with_mention(self.mentions[0])
            eo.entity.kind = EntityKindFactory()
            eo.entity.save()
        self.assertRaises(CoreferenceError, self.merge, self.mentions[:])

    def test_if_only_one_EO_existed_then_all_others_are_created_with_same_entity(self):
        original_eo = self.create_eo_with_mention(self.mentions[0])
        self.merge(self.mentions[:])
        self.assertEqual(self.doc.entity_occurrences.count(), len(self.mentions))
        for eo in self.doc.entity_occurrences.all():
            self.assertEqual(eo.entity, original_eo.entity)
            if eo != original_eo:
                self.assertTrue(eo.anaphora)

    def test_if_all_the_existent_EOs_are_from_anaphora_no_new_ones_are_created(self):
        original_eo = self.create_eo_with_mention(self.mentions[0])
        original_eo.anaphora = True
        original_eo.save()
        self.merge(self.mentions[:])
        self.assertEqual(self.doc.entity_occurrences.count(), 1)

    def test_if_coexist_EO_from_gazette_and_EO_from_NER_entity_of_the_later_is_used(self):
        eo_from_gz = self.create_eo_with_mention(self.mentions[0])
        eo_from_gz.entity.gazette = GazetteItemFactory()
        eo_from_gz.entity.save()
        eo_from_ner = self.create_eo_with_mention(self.mentions[1])
        expected_entity = eo_from_ner.entity
        self.merge(self.mentions[:])
        self.assertEqual(self.doc.entity_occurrences.count(), len(self.mentions))
        for eo in self.doc.entity_occurrences.all():
            # this will reload also eo_from_gz and eo_from_ner
            self.assertEqual(eo.entity, expected_entity)

    def test_if_coexist_several_EOs_from_NER_the_entity_of_first_is_used(self):
        eo_1 = self.create_eo_with_mention(self.mentions[0])
        eo_2 = self.create_eo_with_mention(self.mentions[1])
        assert eo_1.entity != eo_2.entity
        expected_entity = eo_1.entity
        self.merge(self.mentions[:])
        for eo in self.doc.entity_occurrences.all():
            # this will reload eo_1 and eo_2
            self.assertEqual(eo.entity, expected_entity)

    def test_cant_merge_several_EOs_from_different_GZ_items(self):
        eo_1 = self.create_eo_with_mention(self.mentions[0])
        eo_1.entity.gazette = GazetteItemFactory()
        eo_1.entity.save()
        eo_2 = self.create_eo_with_mention(self.mentions[1])
        eo_2.entity.gazette = GazetteItemFactory()
        eo_2.entity.save()
        self.assertRaises(CoreferenceError, self.merge, self.mentions[:])
