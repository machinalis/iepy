# -*- coding: utf-8 -*-
from string import punctuation

from featureforge.vectorizer import Vectorizer
from sklearn.feature_selection import SelectKBest, f_regression
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor


from featureforge.feature import output_schema

__all__ = ["FactExtractorFactory"]

_selectors = {
    "kbest": lambda n: SelectKBest(f_regression, n),
    "dtree": lambda n: DecisionTreeRegressor(),
}

_classifiers = {
    "sgd": SGDClassifier,
    "naivebayes": GaussianNB,
}


class FactExtractor(object):

    def __init__(self, config):
        features = config.get('features', [
            bag_of_words,
            bag_of_pos,
            bag_of_word_bigrams,
            bag_of_wordpos,
            bag_of_wordpos_bigrams,
            bag_of_words_in_between,
            bag_of_pos_in_between,
            bag_of_word_bigrams_in_between,
            bag_of_wordpos_in_between,
            bag_of_wordpos_bigrams_in_between,
            entity_order,
            entity_distance,
            other_entities_in_between,
            in_same_sentence,
            verb_pos_count_in_between,
            verb_pos_count,
            total_number_of_entities,
            symbols_in_between,
            number_of_tokens,
        ])
        classifier = _classifiers[config.get("classifier", "sgd")]
        steps = [
            ('vectorizer', Vectorizer(features)),
            ('scaler', StandardScaler()),
            ('classifier', classifier(**config.get('classifier_args', {})))
        ]
        selector = config.get("dimensionality_reduction")
        if selector is not None:
            n = config['dimensionality_reduction_dimension']
            steps[1:1] = ('dimensionality_reduction', _selectors[selector](n))
        p = Pipeline(steps)
        self.predictor = p

    def fit(self, data):
        X = []
        y = []
        for evidence, score in data.items():
            X.append(evidence)
            y.append(int(score))
        self.predictor.fit(X, y)

    def predict(self, evidences):
        return self.predictor.predict(evidences)


def FactExtractorFactory(config, data):
    """Instantiates and trains a classifier."""
    p = FactExtractor(config)
    p.fit(data)
    return p


###
# FEATURES
###


@output_schema({str})
def bag_of_words(datapoint):
    return set(words(datapoint))


@output_schema({str})
def bag_of_pos(datapoint):
    return set(datapoint.segment.postags)


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_word_bigrams(datapoint):
    return set(bigrams(words(datapoint)))


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_wordpos(datapoint):
    return set(zip(words(datapoint), datapoint.segment.postags))


@output_schema({((str,),)},
               lambda v: all(len(x) == 2 and
                             all(len(y) == 2 for y in x) for x in v))
def bag_of_wordpos_bigrams(datapoint):
    xs = list(zip(words(datapoint), datapoint.segment.postags))
    return set(bigrams(xs))


@output_schema({str})
def bag_of_words_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(words(datapoint)[i:j])


@output_schema({str})
def bag_of_pos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(datapoint.segment.postags[i:j])


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_word_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(bigrams(words(datapoint)[i:j]))


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_wordpos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(list(zip(words(datapoint), datapoint.segment.postags))[i:j])


@output_schema({((str,),)},
               lambda v: all(len(x) == 2 and
                             all(len(y) == 2 for y in x) for x in v))
def bag_of_wordpos_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    xs = list(zip(words(datapoint), datapoint.segment.postags))[i:j]
    return set(bigrams(xs))


@output_schema(int, lambda x: x in (0, 1))
def entity_order(datapoint):
    """
    Returns 1 if A occurs prior to B in the segment and 0 otherwise.
    """
    A, B = get_AB(datapoint)
    if A.offset < B.offset:
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
    for other in datapoint.segment.entities:
        if other.offset >= i and other.offset < j:
            n += 1
    return n


@output_schema(int, lambda x: x>=2)
def total_number_of_entities(datapoint):
    """
    Returns the number of entity in the text segment
    """
    return len(datapoint.segment.entities)


@output_schema(int, lambda x: x>=0)
def verb_pos_count_in_between(datapoint):
    """
    Returns the number of Verb POS tags in between of the 2 entities.
    """
    i, j = in_between_offsets(datapoint)
    return len(list(filter(lambda t: t.startswith('VB'),
                      datapoint.segment.postags[i:j])))


@output_schema(int, lambda x: x>=0)
def verb_pos_count(datapoint):
    """
    Returns the number of Verb POS tags in the datapoint.
    """
    return len(list(filter(lambda t: t.startswith('VB'),
                      datapoint.segment.postags)))


@output_schema(int, lambda x: x in (0, 1))
def in_same_sentence(datapoint):  # TODO: Test
    """
    Returns 1 if the datapoints entities are in the same senteces.
    0 otherwise.
    """
    i, j = in_between_offsets(datapoint)
    for k in datapoint.segment.sentences:
        if i <= k and k < j:
            return 0
    return 1


@output_schema(int, lambda x: x in (0, 1))
def symbols_in_between(datapoint):
    """
    returns 1 if there are symbols between the entities, 0 if not.
    """
    i, j = in_between_offsets(datapoint)
    tokens = datapoint.segment.tokens[i:j]
    punct_set = set(punctuation)
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


def bigrams(xs):
    return list(zip(xs, xs[1:]))


def in_between_offsets(datapoint):
    A, B = get_AB(datapoint)
    if A.offset < B.offset:
        return A.offset_end, B.offset
    return B.offset_end, A.offset


def get_AB(x):
    if x.o1 >= len(x.segment.entities) or x.o2 >= len(x.segment.entities):
        raise ValueError("Invalid entity occurrences")
    return x.segment.entities[x.o1], x.segment.entities[x.o2]
