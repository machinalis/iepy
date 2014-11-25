from collections import defaultdict
from itertools import chain, groupby
import logging
import tempfile

from iepy.preprocess import corenlp
from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps
from iepy.preprocess.ner.base import FoundEntity
from iepy.data.models import Entity, EntityOccurrence, GazetteItem


logger = logging.getLogger(__name__)
GAZETTE_PREFIX = "__GAZETTE_"

class StanfordPreprocess(BasePreProcessStepRunner):

    def __init__(self):
        super().__init__()
        gazettes_filepath = generate_gazettes_file()
        self.corenlp = corenlp.get_analizer(gazettes_filepath=gazettes_filepath)
        self.override = False

    def lemmatization_only(self, document):
        """ Run only the lemmatization """

        # Lemmatization was added after the first so we need to support
        # that a document has all the steps done but lemmatization

        analysis = self.corenlp.analize(document.text)
        sentences = analysis_to_sentences(analysis)
        tokens = get_tokens(sentences)
        if document.tokens != tokens:
            raise ValueError(
                "Document changed since last tokenization, "
                "can't add lemmas to it"
            )
        document.set_lemmatization_result(get_lemmas(sentences))
        document.save()

    def syntactic_parsing_only(self, document):
        """ Run only the syntactic parsing """

        # syntactic parsing was added after the first so we need to support
        # that a document has all the steps done but syntactic parsing

        analysis = self.corenlp.analize(document.text)
        parse_trees = analysis_to_parse_trees(analysis)
        document.set_syntactic_parsing_result(parse_trees)
        document.save()

    def __call__(self, document):
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
        if not self.override:
            # All steps done
            if all(document.was_preprocess_step_done(step) for step in steps):
                return

            # Old steps are the one added up to version 0.9.1
            old_steps = steps[:4]
            done_steps = [step for step in steps if document.was_preprocess_step_done(step)]
            old_steps_done = all([x in done_steps for x in old_steps])

            if old_steps_done:
                if PreProcessSteps.lemmatization not in done_steps:
                    self.lemmatization_only(document)
                if PreProcessSteps.syntactic_parsing not in done_steps:
                    self.syntactic_parsing_only(document)
                return

        if not self.override and document.was_preprocess_step_done(PreProcessSteps.tokenization):
            raise NotImplementedError(
                "Running with mixed preprocess steps not supported, "
                "must be 100% StanfordMultiStepRunner"
            )

        analysis = self.corenlp.analize(document.text)
        sentences = analysis_to_sentences(analysis)
        parse_trees = analysis_to_parse_trees(analysis)

        # Tokenization
        tokens = get_tokens(sentences)
        offsets = get_token_offsets(sentences)
        document.set_tokenization_result(list(zip(offsets, tokens)))

        # Lemmatization
        document.set_lemmatization_result(get_lemmas(sentences))

        # "Sentencing" (splitting in sentences)
        document.set_sentencer_result(get_sentence_boundaries(sentences))

        # POS tagging
        document.set_tagging_result(get_pos(sentences))

        # Syntactic parsing
        document.set_syntactic_parsing_result(parse_trees)

        # NER
        found_entities = get_found_entities(document, sentences, tokens)
        document.set_ner_result(found_entities)

        # Save progress so far, next step doesn't modify `document`
        document.save()

        # Coreference resolution
        for coref in get_coreferences(analysis):
            try:
                apply_coreferences(document, coref)
            except CoreferenceError as e:
                logger.warning(e)


def _dictpath(d, *args):
    x = d
    for key in args:
        try:
            x = x[key]
        except KeyError:
            return []
    if not isinstance(x, list):
        x = [x]
    return x


def analysis_to_sentences(analysis):
    result = []
    sentences = _dictpath(analysis, "sentences", "sentence")
    for sentence in sentences:
        xs = []
        tokens = _dictpath(sentence, "tokens", "token")
        for t in tokens:
            xs.append(t)
        result.append(xs)
    return result

def analysis_to_parse_trees(analysis):
    sentences = _dictpath(analysis, "sentences", "sentence")
    result = [x["parse"] for x in sentences]
    return result


def get_tokens(sentences):
    return [x["word"] for x in chain.from_iterable(sentences)]


def get_lemmas(sentences):
    return [x["lemma"] for x in chain.from_iterable(sentences)]


def get_token_offsets(sentences):
    return [int(x["CharacterOffsetBegin"]) for x in chain.from_iterable(sentences)]


def get_pos(sentences):
    return [x["POS"] for x in chain.from_iterable(sentences)]


def get_sentence_boundaries(sentences):
    """
    Returns a list with the offsets in tokens where each sentence starts, in
    order. The list contains one extra element at the end containing the total
    number of tokens.
    """
    ys = [0]
    for x in sentences:
        y = ys[-1] + len(x)
        ys.append(y)
    return ys


def get_entity_occurrences(sentences):
    """
    Returns a list of tuples (i, j, kind) such that `i` is the start
    offset of an entity occurrence, `j` is the end offset and `kind` is the
    entity kind of the entity.
    """
    found_entities = []
    offset = 0
    for words in sentences:
        for kind, group in groupby(enumerate(words), key=lambda x: x[1]["NER"]):
            if kind == "O":
                continue
            ix = [i for i, word in group]
            i = ix[0] + offset
            j = ix[-1] + 1 + offset
            found_entities.append((i, j, kind))
        offset += len(words)
    return found_entities


def get_found_entities(document, sentences, tokens):
    """
    Generates FoundEntity objects for the entities found.
    For all the entities that came from a gazette, joins
    the ones with the same kind.
    """

    found_entities = []
    for i, j, kind in get_entity_occurrences(sentences):
        alias = " ".join(tokens[i:j])
        if kind.startswith(GAZETTE_PREFIX):
            kind = kind.split(GAZETTE_PREFIX, 1)[1]
            key = "{}{}_{}".format(
                GAZETTE_PREFIX, kind, alias
            )
        else:
            key = "{} {} {} {}".format(
                document.human_identifier, kind, i, j
            )

        found_entities.append(FoundEntity(
            key=key,
            kind_name=kind,
            alias=alias,
            offset=i,
            offset_end=j
        ))
    return found_entities


def get_coreferences(analysis):
    """
    Returns a list of lists of tuples (i, j, k) such that `i` is the start
    offset of a reference, `j` is the end offset and `k` is the index of the
    head word within the reference.
    All offsets are in tokens and relative to the start of the document.
    All references within the same list refer to the same entity.
    All references in different lists refer to different entities.
    """
    sentences = analysis_to_sentences(analysis)
    sentence_offsets = get_sentence_boundaries(sentences)
    coreferences = []
    for mention in _dictpath(analysis, "coreference", "coreference"):
        occurrences = []
        representative = 0
        for r, occurrence in enumerate(_dictpath(mention, "mention")):
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


def apply_coreferences(document, coreferences):
    """
    Makes all entity ocurrences named in `coreference` have the same
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
    missing = []  # References that have no entity occurrence yet
    for i, j, head in coreferences:
        if occurrences[head]:
            entities.extend(x.entity for x in occurrences[head])
        else:
            missing.append((i, j, head))

    if not entities:
        return
    if len(set(e.kind for e in entities)) != 1:
        raise CoreferenceError("Cannot merge entities of different kinds {!r}".format(set(e.kind for e in entities)))

    # Select canonical name for the entity
    i, j, _ = coreferences[0]
    name = " ".join(document.tokens[i:j])
    # Select canonical entity, every occurrence will point to this entity
    try:
        canonical = Entity.objects.get(key=name)
    except Entity.DoesNotExist:
        canonical = entities[0]

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
            alias=" ".join(document.tokens[i:j]))

    # Finally, the merging 'per se', where all things are entity ocurrences
    for entity in set(x for x in entities if x != canonical):
        for occurrence in EntityOccurrence.objects.filter(entity=entity):
            occurrence.entity = canonical
            occurrence.save()


def generate_gazettes_file():
    """
    Generates the gazettes file if there's any. Returns
    the filepath in case gazettes where found, else None.
    """
    gazettes = GazetteItem.objects.all()
    if not gazettes.count():
        return

    gazette_format = "{}\t{}\n"
    _, filepath = tempfile.mkstemp()
    with open(filepath, "w") as gazette_file:
        for gazette in gazettes:
            kind = "{}{}".format(GAZETTE_PREFIX, gazette.kind.name.replace("\t", " "))
            text = gazette.text.replace("\t", " ")
            line = gazette_format.format(text, kind)
            gazette_file.write(line)
    return filepath


class CoreferenceError(Exception):
    pass
