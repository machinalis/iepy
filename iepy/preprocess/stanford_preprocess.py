from collections import defaultdict
from itertools import chain, groupby
import logging
import tempfile

from iepy.preprocess import corenlp
from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps
from iepy.preprocess.ner.base import FoundEntity
from iepy.data.models import EntityOccurrence, GazetteItem


logger = logging.getLogger(__name__)


class CoreferenceError(Exception):
    pass


class GazetteManager:
    _PREFIX = "__GAZETTE_"

    # Stanford NER default/native classes
    NATIVE_CLASSES = [
        'DATE', 'DURATION', 'LOCATION', 'MISC',
        'MONEY', 'NUMBER', 'ORDINAL', 'ORGANIZATION',
        'PERCENT', 'PERSON', 'SET', 'TIME',
    ]

    def __init__(self):
        self.gazette_items = list(GazetteItem.objects.all())
        self._cache_per_kind = defaultdict(list)

    def escape_text(self, text):
        text = " ".join("\Q{}\E".format(x) for x in text.split())
        return text

    def strip_kind(self, prefixed_kind):
        return prefixed_kind.split(self._PREFIX, 1)[-1]

    def was_entry_created_by_gazette(self, alias, kind):
        if kind.startswith(self._PREFIX):
            return True
        return alias in self._cache_per_kind[kind]

    def generate_stanford_gazettes_file(self):
        """
        Generates the gazettes file if there's any. Returns
        the filepath in case gazette items where found, else None.

        Note: the Stanford Coreference annotator, only handles Entities of their
        native classes. That's why there's some special management of Gazette items
        of such classes/kinds.
        As a side effect, populates the internal cache with the gazette-items
        that will be passed to Stanford with any of their Native classes (Entity Kinds)
        """
        if not self.gazette_items:
            return

        overridable_classes = ",".join(self.NATIVE_CLASSES)
        self._cache_per_kind = defaultdict(list)

        gazette_format = "{}\t{}\t{}\n"
        _, filepath = tempfile.mkstemp()
        with open(filepath, "w") as gazette_file:
            for gazette in self.gazette_items:
                kname = gazette.kind.name
                if kname in self.NATIVE_CLASSES:
                    # kind will not be escaped, but tokens will be stored on cache
                    self._cache_per_kind[kname].append(gazette.text)
                else:
                    kname = "{}{}".format(self._PREFIX, kname)
                text = self.escape_text(gazette.text)
                line = gazette_format.format(text, kname, overridable_classes)
                gazette_file.write(line)
        return filepath


class StanfordPreprocess(BasePreProcessStepRunner):

    def __init__(self, increment_ner=False):
        super().__init__()
        self.gazette_manager = GazetteManager()
        gazettes_filepath = self.gazette_manager.generate_stanford_gazettes_file()
        self.corenlp = corenlp.get_analizer(gazettes_filepath=gazettes_filepath)
        self.override = False
        self.increment_ner = increment_ner

    def lemmatization_only(self, document):
        """ Run only the lemmatization """
        # Lemmatization was added after the first so we need to support
        # that a document has all the steps done but lemmatization

        analysis = StanfordAnalysis(self.corenlp.analyse(document.text))
        tokens = analysis.get_tokens()
        if document.tokens != tokens:
            raise ValueError(
                "Document changed since last tokenization, "
                "can't add lemmas to it"
            )
        document.set_lemmatization_result(analysis.get_lemmas())
        document.save()

    def syntactic_parsing_only(self, document):
        """ Run only the syntactic parsing """
        # syntactic parsing was added after the first release, so we need to
        # provide the ability of doing just this on documents that
        # have all the steps done but syntactic parsing
        analysis = StanfordAnalysis(self.corenlp.analyse(document.text))
        parse_trees = analysis.get_parse_trees()
        document.set_syntactic_parsing_result(parse_trees)
        document.save()

    def increment_ner_only(self, document):
        """
        Runs NER steps (basic NER and also Gazetter), adding the new found NE.
        """
        analysis = StanfordAnalysis(self.corenlp.analyse(document.text))

        # NER
        found_entities = analysis.get_found_entities(
            document.human_identifier, self.gazette_manager
        )
        document.set_ner_result(found_entities)

        # Save progress so far, next step doesn't modify `document`
        document.save()

        # Coreference resolution
        for coref in analysis.get_coreferences():
            try:
                apply_coreferences(document, coref)
            except CoreferenceError as e:
                logger.warning(e)

    def __call__(self, document):
        """Checks state of the document, and based on the preprocess options,
        # decides what needs to be run, and triggers it.
        """
        steps = [
            PreProcessSteps.tokenization,
            PreProcessSteps.sentencer,
            PreProcessSteps.tagging,
            PreProcessSteps.ner,
            # Steps added after 0.9.1
            PreProcessSteps.lemmatization,
            # Steps added after 0.9.2
            PreProcessSteps.syntactic_parsing,
        ]

        steps_done = set([s for s in steps if document.was_preprocess_step_done(s)])

        if self.override or not steps_done:
            # no matter what's the internal state of the document, or any other option
            # on the StanfordPreprocess, everything need to be run
            self.run_everything(document)
        elif steps_done == set(steps):
            # All steps are already done...
            if self.increment_ner:
                self.increment_ner_only(document)
        else:
            # Dealing with accepting "incremental-running" of preprocess for documents
            # that were preprocessed with some older version of IEPY.

            # "initial_steps" are the ones added up to version 0.9.1, which (at some point)
            # were considered "all available steps".
            initial_steps = steps[:4]
            all_initials_done = set(initial_steps).issubset(steps_done)

            if all_initials_done:
                if PreProcessSteps.lemmatization not in steps_done:
                    self.lemmatization_only(document)
                if PreProcessSteps.syntactic_parsing not in steps_done:
                    self.syntactic_parsing_only(document)
            else:
                # weird combination of steps done. We can't handle that right now
                raise NotImplementedError(
                    "Running with mixed preprocess steps not supported, "
                    "must be 100% StanfordMultiStepRunner"
                )

    def run_everything(self, document):
        analysis = StanfordAnalysis(self.corenlp.analyse(document.text))

        # Tokenization
        tokens = analysis.get_tokens()
        offsets = analysis.get_token_offsets()
        document.set_tokenization_result(list(zip(offsets, tokens)))

        # Lemmatization
        document.set_lemmatization_result(analysis.get_lemmas())

        # "Sentencing" (splitting in sentences)
        document.set_sentencer_result(analysis.get_sentence_boundaries())

        # POS tagging
        document.set_tagging_result(analysis.get_pos())

        # Syntactic parsing
        document.set_syntactic_parsing_result(analysis.get_parse_trees())

        # NER
        found_entities = analysis.get_found_entities(
            document.human_identifier, self.gazette_manager
        )
        document.set_ner_result(found_entities)

        # Save progress so far, next step doesn't modify `document`
        document.save()

        # Coreference resolution
        for coref in analysis.get_coreferences():
            try:
                apply_coreferences(document, coref)
            except CoreferenceError as e:
                logger.warning(e)


def _dict_path(d, *steps):
    """Traverses throuth a dict of dicts.
    Returns always a list. If the object to return is not a list,
    it's encapsulated in one.
    If any of the path steps does not exist, an empty list is returned.
    """
    x = d
    for key in steps:
        try:
            x = x[key]
        except KeyError:
            return []
    if not isinstance(x, list):
        x = [x]
    return x


class StanfordAnalysis:
    """Helper for extracting the information from stanford corenlp output"""

    def __init__(self, data):
        self._data = data
        self.sentences = self.get_sentences()
        self._raw_tokens = list(chain.from_iterable(self.sentences))

    def _get(self, *args):
        return _dict_path(self._data, *args)

    def get_sentences(self):
        result = []
        raw_sentences = self._get("sentences", "sentence")
        for sentence in raw_sentences:
            xs = []
            tokens = _dict_path(sentence, "tokens", "token")
            for t in tokens:
                xs.append(t)
            result.append(xs)
        return result

    def get_sentence_boundaries(self):
        """
        Returns a list with the offsets in tokens where each sentence starts, in
        order. The list contains one extra element at the end containing the total
        number of tokens.
        """
        ys = [0]
        for x in self.sentences:
            y = ys[-1] + len(x)
            ys.append(y)
        return ys

    def get_parse_trees(self):
        result = [x["parse"] for x in self._get("sentences", "sentence")]
        return result

    def get_tokens(self):
        return [x["word"] for x in self._raw_tokens]

    def get_lemmas(self):
        return [x["lemma"] for x in self._raw_tokens]

    def get_token_offsets(self):
        return [int(x["CharacterOffsetBegin"]) for x in self._raw_tokens]

    def get_pos(self):
        return [x["POS"] for x in self._raw_tokens]

    def get_found_entities(self, entity_key_prefix, gazette_manager=None):
        """
        Generates FoundEntity objects for the entities found.
        For all the entities that came from a gazette, joins
        the ones with the same kind.
        """
        found_entities = []
        tokens = self.get_tokens()
        for i, j, kind in self.get_entity_occurrences():
            alias = " ".join(tokens[i:j])

            if gazette_manager is not None:
                from_gazette = gazette_manager.was_entry_created_by_gazette(alias, kind)
            else:
                from_gazette = False

            if from_gazette:
                kind = gazette_manager.strip_kind(kind)
                key = alias
            else:
                key = "{} {} {} {}".format(entity_key_prefix, kind, i, j)

            found_entities.append(FoundEntity(
                key=key,
                kind_name=kind,
                alias=alias,
                offset=i,
                offset_end=j,
                from_gazette=from_gazette
            ))
        return found_entities

    def get_entity_occurrences(self):
        """
        Returns a list of tuples (i, j, kind) such that `i` is the start
        offset of an entity occurrence, `j` is the end offset and `kind` is the
        entity kind of the entity.
        """
        found_entities = []
        offset = 0
        for words in self.sentences:
            for kind, group in groupby(enumerate(words), key=lambda x: x[1]["NER"]):
                if kind == "O":
                    continue
                ix = [i for i, word in group]
                i = ix[0] + offset
                j = ix[-1] + 1 + offset
                found_entities.append((i, j, kind))
            offset += len(words)
        return found_entities

    def get_coreferences(self):
        """
        Returns a list of lists of tuples (i, j, k) such that `i` is the start
        offset of a reference, `j` is the end offset and `k` is the index of the
        head word within the reference.
        All offsets are in tokens and relative to the start of the document.
        All references within the same list refer to the same entity.
        All references in different lists refer to different entities.
        """
        sentence_offsets = self.get_sentence_boundaries()
        coreferences = []
        for mention in self._get("coreference", "coreference"):
            occurrences = []
            representative = 0
            for r, occurrence in enumerate(_dict_path(mention, "mention")):
                if "@representative" in occurrence:
                    representative = r
                sentence = int(occurrence["sentence"]) - 1
                offset = sentence_offsets[sentence]
                i = int(occurrence["start"]) - 1 + offset
                j = int(occurrence["end"]) - 1 + offset
                k = int(occurrence["head"]) - 1 + offset
                occurrences.append((i, j, k))
            # Occurrences' representative goes in the first position
            k = representative
            occurrences[0], occurrences[k] = occurrences[0], occurrences[k]
            coreferences.append(occurrences)
        return coreferences


def issues_merging_entities(document, entities):
    # Checks is some general preconditions are met before proceeding to merge some
    # entities on a fiven document
    kinds = set(e.kind for e in entities)
    if len(kinds) != 1:
        return "Cannot merge entities of different kinds {!r}".format(kinds)
    gazettes = set(e.gazette for e in entities if e.gazette)
    if len(gazettes) > 1:
        return "Cannot merge entities of different gazette items {!r}".format(gazettes)


def apply_coreferences(document, coreferences):
    """
    Makes all entity ocurrences listed in `coreferences` have the same
    entity.
    It uses coreference information to merge entity ocurrence's
    entities into a single entity.
    `correferences` is a list of tuples (i, j, head) where:
     - `i` is the offset in tokens where the occurrence starts.
     - `j` is the offset in tokens where the occurrence ends.
     - `head` is the index in tokens of the head of the occurrence (the "most
        important word").

    Every entity occurrence in `coreference` might already exist or not in
    `document`. If no occurrence exists in `document` then nothing is done.
    If at least one ocurrence exists in `document` then all other ocurrences
    named in `coreference` are automatically created.

    This function can raise CofererenceError in case a merge is attempted on
    entities of different kinds.
    """
    # For each token index make a list of the occurrences there
    occurrences = defaultdict(list)
    for occurrence in document.entity_occurrences.all():
        for i in range(occurrence.offset, occurrence.offset_end):
            occurrences[i].append(occurrence)

    entities = []  # Existing entities referenced by correferences
    pickable_as_representant = []
    missing = []  # References that have no entity occurrence yet
    for i, j, head in sorted(coreferences):
        if occurrences[head]:
            for x in occurrences[head]:
                entities.append(x.entity)
                if not x.anaphora:
                    pickable_as_representant.append(x.entity)
        else:
            missing.append((i, j, head))

    if not pickable_as_representant:
        return
    issues = issues_merging_entities(document, entities)
    if issues:
        raise CoreferenceError(issues)

    from_ner = [r for r in pickable_as_representant if not r.gazette]
    if from_ner:
        canonical = from_ner[0]
    else:
        canonical = pickable_as_representant[0]

    # Each missing coreference needs to be created into an occurrence now
    for i, j, head in missing:
        if j - i >= 5:  # If the entity is a long phrase then just keep one token
            i = head
            j = head + 1
        EntityOccurrence.objects.get_or_create(
            document=document,
            entity=canonical,
            offset=i,
            offset_end=j,
            alias=" ".join(document.tokens[i:j]),
            defaults={'anaphora': True})

    # Finally, the merging 'per se', where all things are entity occurrences
    for entity in set(x for x in entities if x != canonical):
        for occurrence in EntityOccurrence.objects.filter(entity=entity,
                                                          document=document):
            occurrence.entity = canonical
            occurrence.save()
