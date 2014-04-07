# -*- coding: utf-8 -*-
from featureforge.vectorizer import Vectorizer
from sklearn.feature_selection import SelectKBest
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeRegressor

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
        return self.predictor(evidences)


def FactExtractorFactory(config, data):  # TODO: Remove relation
    """Instantiates and trains a classifier."""
    p = FactExtractor(config)
    p.fit(data)
    return p


###
# FEATURES
###


def bag_of_words(datapoint):
    return set(words(datapoint))


def bag_of_pos(datapoint):
    return set(datapoint.segment.postags)


def bag_of_word_bigrams(datapoint):
    return set(bigrams(words(datapoint)))


def bag_of_wordpos(datapoint):
    return set(zip(words(datapoint), datapoint.segment.postags))


def bag_of_wordpos_bigrams(datapoint):
    xs = list(zip(words(datapoint), datapoint.segment.postags))
    return set(bigrams(xs))


def bag_of_words_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(words(datapoint)[i:j])


def bag_of_pos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(datapoint.segment.postags[i:j])


def bag_of_word_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(bigrams(words(datapoint))[i:j])


def bag_of_wordpos_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    return set(zip(words(datapoint), datapoint.segment.postags)[i:j])


def bag_of_wordpos_bigrams_in_between(datapoint):
    i, j = in_between_offsets(datapoint)
    xs = list(zip(words(datapoint), datapoint.segment.postags))
    return set(bigrams(xs)[i:j])


def entity_order(datapoint):
    """
    Returns 1 if A occurs prior to B in the segment and 0 otherwise.
    """
    A, B = get_AB(datapoint)
    if A.offset < B.offset:
        return 1
    return 0


def entity_distance(datapoint):
    """
    Returns the distance (in tokens) that separates the ocurrence of the
    entities.
    """
    i, j = in_between_offsets(datapoint)
    return j - i


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
    return zip(xs, xs[1:])


def in_between_offsets(datapoint):
    A, B = get_AB(datapoint)
    if A.offset < B.offset:
        return A.offset_end, B.offset
    return B.offset_end, A.offset


def get_AB(x):
    return x.segment.entities[x.o1], x.segment.entities[x.o2]

