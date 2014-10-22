import ast
from string import punctuation

from featureforge.feature import output_schema, Feature
from schema import Schema, And


punct_set = set(punctuation)


def parse_features(feature_names):
    features = []
    for line in feature_names:
        if not line or line != line.strip():
            raise ValueError("Garbage in feature set: {!r}".format(line))
        fname, _, args = line.partition(" ")
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


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_word_bigrams(datapoint):
    return set(bigrams(words(datapoint)))


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_wordpos(datapoint):
    return set(zip(words(datapoint), pos(datapoint)))


@output_schema({((str,),)},
               lambda v: all(len(x) == 2 and
                             all(len(y) == 2 for y in x) for x in v))
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


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_word_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(bigrams(words(datapoint)[i:j]))


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_wordpos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(list(zip(words(datapoint), pos(datapoint)))[i:j])


@output_schema({((str,),)},
               lambda v: all(len(x) == 2 and
                             all(len(y) == 2 for y in x) for x in v))
def bag_of_wordpos_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    xs = list(zip(words(datapoint), pos(datapoint)))[i:j]
    return set(bigrams(xs))


@output_schema(int, lambda x: x in (0, 1))
def entity_order(datapoint):
    """
    Returns 1 if A occurs prior to B in the segment and 0 otherwise.
    """
    A, B = get_AB(datapoint)
    if A.segment_offset < B.segment_offset:
        return 1
    return 0


@output_schema(int, lambda x: x >= 0)
def entity_distance(datapoint):
    """
    Returns the distance (in tokens) that separates the ocurrence of the
    entities.
    """
    i, j = in_between_offsets(datapoint)
    return j - i


@output_schema(int, lambda x: x >= 0)
def other_entities_in_between(datapoint):
    """
    Returns the number of entity ocurrences in between the datapoint entities.
    """
    n = 0
    i, j = in_between_offsets(datapoint)
    for other in datapoint.segment.entity_occurrences.all():
        other.hydrate_for_segment(datapoint.segment)
        if other.segment_offset >= i and other.segment_offset < j:
            n += 1
    return n


@output_schema(int, lambda x: x >= 2)
def total_number_of_entities(datapoint):
    """
    Returns the number of entity in the text segment
    """
    return len(datapoint.segment.entity_occurrences.all())


@output_schema(int, lambda x: x >= 0)
def verbs_count_in_between(datapoint):
    """
    Returns the number of Verb POS tags in between of the 2 entities.
    """
    i, j = in_between_offsets(datapoint)
    return len(verbs(datapoint, i, j))


@output_schema(int, lambda x: x >= 0)
def verbs_count(datapoint):
    """
    Returns the number of Verb POS tags in the datapoint.
    """
    return len(verbs(datapoint))


class BaseBagOfVerbs(Feature):
    output_schema = Schema({str})

    def _evaluate(self, datapoint):
        i, j = None, None
        if self.in_between:
            i, j = in_between_offsets(datapoint)
        verb_tokens = verbs(datapoint, i, j)
        return set([self.do(tk) for tk in verb_tokens])


class LemmaBetween(Feature):
    output_schema = Schema(And(int, lambda x: x in (0, 1)))

    def __init__(self, lemma):
        self.lemma = lemma

    def _evaluate(self, datapoint):
        i, j = in_between_offsets(datapoint)
        if self.lemma in datapoint.segment.tokens[i:j]:
            return 1
        else:
            return 0

    def name(self):
        return u'<LemmaBetween, lemma=%s>' % self.lemma


@output_schema(int, lambda x: x in (0, 1))
def in_same_sentence(datapoint):  # TODO: Test
    """
    Returns 1 if the datapoints entities are in the same sentence, 0 otherwise.
    """
    i, j = in_between_offsets(datapoint)
    for k in datapoint.segment.sentences:
        if i <= k and k < j:
            return 0
    return 1


@output_schema(int, lambda x: x in (0, 1))
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


@output_schema(int, lambda x: x >= 0)
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
