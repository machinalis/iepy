# -*- coding: utf-8 -*-
from sklearn.linear_model import SGDClassifier
from featureforge.vectorizer import Vectorizer
<<<<<<< Updated upstream
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeRegressor
=======
from featureforge.feature import input_schema, output_schema, ObjectSchema

from sklearn.pipeline import Pipeline

>>>>>>> Stashed changes

__all__ = ["FactExtractorFactory"]

_selectors = {
    "kbest": lambda n: SelectKBest(f_regression, n),
    "dtree": lambda n: DecisionTreeRegressor(),
}

_classifiers = {
    "sgd": SGDClassifier,
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
        ])
        classifier = _classifiers[config.get("classifier", "sgd")]
        steps = [
            ('vectorizer', Vectorizer(features)),
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


def _evidence_schema(**kwargs):
    schema = {}
    for k, v in kwargs.iteritems():
        if isinstance(k, tuple):
            assert len(k) >= 1, "schema not meant to be used this way"
            if len(k) > 1:
                #v = _evidence_schema(**{k[1:]=v})
                pass
            k = k[0]
        assert k not in schema, "schema not meant to be used this way"
        schema[k] = v
    return ObjectSchema(**schema)


def evidence_input_schema(**kwargs):
    def decorate(f):
        return input_schema(_evidence_schema(**kwargs))(f)
    return decorate


#@evidence_input_schema(("segment", "tokens")=[str])
@output_schema({str})
def bag_of_words(*datapoint):
    print(repr(datapoint), repr(datapoint[0]), type(datapoint[0]))
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
    return set(bigrams(words(datapoint))[i:j])


@output_schema({(str,)}, lambda v: all(len(x) == 2 for x in v))
def bag_of_wordpos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(list(zip(words(datapoint), datapoint.segment.postags))[i:j])


@output_schema({((str,),)},
               lambda v: all(len(x) == 2 and
                             all(len(y) == 2 for y in x) for x in v))
def bag_of_wordpos_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    xs = list(zip(words(datapoint), datapoint.segment.postags))
    return set(bigrams(xs)[i:j])


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


@output_schema(int, lambda x: x in (0, 1))
def in_same_sentence(datapoint):
    """
    Returns 1 if the datapoints entities are in the same senteces.
    0 otherwise.
    """
    i, j = in_between_offsets(datapoint)
    for k in datapoint.segment.sentences:
        if i <= k and k < j:
            return 0
    return 1


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
    return x.segment.entities[x.o1], x.segment.entities[x.o2]
