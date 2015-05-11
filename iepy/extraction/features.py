import ast
from string import punctuation
import importlib

import refo
from featureforge.feature import output_schema

from iepy.extraction.rules import generate_tokens_to_match, compile_rule
from iepy.data.models import Relation

punct_set = set(punctuation)


def all_len_two(v):
    return all(len(x) == 2 for x in v)


def all_len_two_inner_too(v):
    return all(len(x) == 2 and all(len(y) == 2 for y in x) for x in v)


def binary_values(x):
    return x in (0, 1)


def ge_than_zero(v):
    return v >= 0


def ge_than_two(v):
    return v >= 2


_loaded_modules = {}
def load_module(module_name):
    module = _loaded_modules.get(module_name)
    if module is None:
        module = importlib.import_module(module_name)
        _loaded_modules[module_name] = module
    return module


def rule_wrapper(rule_feature, relation):
    @output_schema(int, binary_values)
    def inner(evidence):
        regex = compile_rule(rule_feature, relation)
        tokens_to_match = generate_tokens_to_match(evidence)
        return int(bool(refo.match(regex, tokens_to_match)))
    return inner


def parse_features(feature_names):
    features = []
    for line in feature_names:
        if not line or line != line.strip():
            raise ValueError("Garbage in feature set: {!r}".format(line))
        fname, _, args = line.partition(" ")

        if fname.count("."):  # Is a module path
            feature_module, feature_name = fname.rsplit(".", 1)
            try:
                module = load_module(feature_module)
            except ImportError:
                raise KeyError("Couldn't load module {!r}".format(feature_module))

            try:
                feature = getattr(module, feature_name)
            except AttributeError:
                raise KeyError(
                    "Feature {!r} not found in {!r} module".format(feature_name, feature_module)
                )

            if feature_module.endswith(".rules"):
                relation = Relation.objects.get(name=module.RELATION)
                feature = rule_wrapper(feature, relation)
        else:
            try:
                feature = globals()[fname]
            except KeyError:
                raise KeyError("There is not such feature: "
                               "{!r}".format(fname))
        args = args.strip()
        if args:
            args = ast.literal_eval(args + ",")
            feature = feature(*args)
        features.append(feature)
    return features


@output_schema({str})
def bag_of_words(datapoint):
    return set(words(datapoint))


@output_schema({str})
def bag_of_pos(datapoint):
    return set(pos(datapoint))


@output_schema({(str,)}, all_len_two)
def bag_of_word_bigrams(datapoint):
    return set(bigrams(words(datapoint)))


@output_schema({(str,)}, all_len_two)
def bag_of_wordpos(datapoint):
    return set(zip(words(datapoint), pos(datapoint)))


@output_schema({((str,),)}, all_len_two_inner_too)
def bag_of_wordpos_bigrams(datapoint):
    xs = list(zip(words(datapoint), pos(datapoint)))
    return set(bigrams(xs))


@output_schema({str})
def bag_of_words_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(words(datapoint)[i:j])


@output_schema({str})
def bag_of_pos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(pos(datapoint)[i:j])


@output_schema({(str,)}, all_len_two)
def bag_of_word_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(bigrams(words(datapoint)[i:j]))


@output_schema({(str,)}, all_len_two)
def bag_of_wordpos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(list(zip(words(datapoint), pos(datapoint)))[i:j])


@output_schema({((str,),)}, all_len_two_inner_too)
def bag_of_wordpos_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    xs = list(zip(words(datapoint), pos(datapoint)))[i:j]
    return set(bigrams(xs))


@output_schema(int, binary_values)
def entity_order(datapoint):
    """
    Returns 1 if A occurs prior to B in the segment and 0 otherwise.
    """
    A, B = get_AB(datapoint)
    if A.segment_offset < B.segment_offset:
        return 1
    return 0


@output_schema(int, ge_than_zero)
def entity_distance(datapoint):
    """
    Returns the distance (in tokens) that separates the ocurrence of the
    entities.
    """
    i, j = in_between_offsets(datapoint)
    return j - i


@output_schema(int, ge_than_zero)
def other_entities_in_between(datapoint):
    """
    Returns the number of entity ocurrences in between the datapoint entities.
    """
    n = 0
    i, j = in_between_offsets(datapoint)
    for other in datapoint.all_eos:
        if other.segment_offset >= i and other.segment_offset < j:
            n += 1
    return n


@output_schema(int, ge_than_two)
def total_number_of_entities(datapoint):
    """
    Returns the number of entity in the text segment
    """
    return len(datapoint.all_eos)


@output_schema(int, ge_than_zero)
def verbs_count_in_between(datapoint):
    """
    Returns the number of Verb POS tags in between of the 2 entities.
    """
    i, j = in_between_offsets(datapoint)
    return len(verbs(datapoint, i, j))


@output_schema(int, ge_than_zero)
def verbs_count(datapoint):
    """
    Returns the number of Verb POS tags in the datapoint.
    """
    return len(verbs(datapoint))


@output_schema(int, binary_values)
def in_same_sentence(datapoint):  # TODO: Test
    """
    Returns 1 if the datapoints entities are in the same sentence, 0 otherwise.
    """
    i, j = in_between_offsets(datapoint)
    for k in datapoint.segment.sentences:
        if i <= k and k < j:
            return 0
    return 1


@output_schema(int, binary_values)
def symbols_in_between(datapoint):
    """
    Returns 1 if there are symbols between the entities, 0 if not.
    """
    i, j = in_between_offsets(datapoint)
    tokens = datapoint.segment.tokens[i:j]
    for tkn in tokens:
        if punct_set.intersection(tkn):
            return 1
    return 0


@output_schema(int, ge_than_zero)
def number_of_tokens(datapoint):
    return len(datapoint.segment.tokens)


###
# Aux functions
###

def words(datapoint):
    return [word.lower() for word in datapoint.segment.tokens]


def pos(datapoint):
    return list(map(str, datapoint.segment.postags))


def verbs(datapoint, slice_i=0, slice_j=None):
    pairs = zip(datapoint.segment.tokens, datapoint.segment.postags)
    if slice_j is not None:
        pairs = list(pairs)[slice_i:slice_j]
    return [tkn for tkn, tag in pairs if tag.startswith(u'VB')]


def bigrams(xs):
    return list(zip(xs, xs[1:]))


def in_between_offsets(datapoint):
    A, B = get_AB(datapoint)
    if A.segment_offset_end < B.segment_offset:
        return A.segment_offset_end, B.segment_offset
    elif B.segment_offset_end < A.segment_offset:
        return B.segment_offset_end, A.segment_offset
    elif A.segment_offset_end < B.segment_offset_end:
        return A.segment_offset_end, A.segment_offset_end
    return B.segment_offset_end, B.segment_offset_end


def get_AB(datapoint):
    a = datapoint.right_entity_occurrence
    b = datapoint.left_entity_occurrence
    return a, b
