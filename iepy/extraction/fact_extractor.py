# -*- coding: utf-8 -*-
import ast
from string import punctuation

from featureforge.feature import output_schema, Feature
from featureforge.vectorizer import Vectorizer
from nltk.stem.lancaster import LancasterStemmer
from nltk.stem import WordNetLemmatizer
from schema import Schema, And
from sklearn.feature_selection import SelectKBest, chi2
from sklearn.pipeline import Pipeline
from sklearn.linear_model import SGDClassifier
from sklearn.naive_bayes import GaussianNB, MultinomialNB
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.manifold import SpectralEmbedding
from sklearn.decomposition import TruncatedSVD, NMF, PCA
from sklearn.svm import SVC
from sklearn.ensemble import AdaBoostClassifier
from sklearn.semi_supervised.label_propagation import LabelSpreading
from numpy import array
from scipy.sparse import issparse

from future.builtins import map, str


class MoreSamplesNeededException(Exception):
    pass


def adawrapper(**kwargs):
    base = {}
    estimator = dict(kwargs)
    for k in ["n_estimators", "learning_rate"]:
        if k in estimator:
            base[k] = estimator[k]
            del estimator[k]
    return AdaBoostClassifier(DecisionTreeClassifier(**estimator), **base)


__all__ = ["FactExtractorFactory"]


_selectors = {
    "kbest": lambda n: SelectKBest(chi2, n),
    "dtree": lambda n: DecisionTreeClassifier(),
    "frequency_filter": lambda n: ColumnFilter(n),
}

_dimensionality_reduction = {
    "svd": lambda n: TruncatedSVD(n),
    "spectralembbeding": lambda n: SpectralEmbedding(n),
    "nmf": lambda n: NMF(n),
    "pca": lambda n: PCA(n),
}

_classifiers = {
    "sgd": SGDClassifier,
    "naivebayes": GaussianNB,
    "naivebayes_m": MultinomialNB,
    "dtree": DecisionTreeClassifier,
    "logit": LogisticRegression,
    "svm": SVC,
    "adaboost": adawrapper,
    "labelspreading": LabelSpreading,
}

_configuration_options = """
    feature_selection
    feature_selection_dimension
    dimensionality_reduction
    dimensionality_reduction_dimension
    scaler
    classifier
    classifier_args
    features
    sparse
""".split()


class FactExtractor(object):

    def __init__(self, config):
        # Validate options are present
        for option in _configuration_options:
            if option not in config:
                raise ValueError("Missing configuration "
                                 "option {!r}".format(option))

        # Feature selection
        selector = config["feature_selection"]
        seln = config["feature_selection_dimension"]
        if selector is not None:
            try:
                selector = _selectors[selector](seln)
            except KeyError:
                raise ValueError("Unknown feature selection method "
                                 "{!r}".format(selector))

        # Dimensionality reduction
        dimred = config["dimensionality_reduction"]
        dimredn = config["dimensionality_reduction_dimension"]
        if dimred is not None:
            try:
                dimred = _dimensionality_reduction[dimred](dimredn)
            except KeyError:
                raise ValueError("Unknown dimensionality reduction method"
                                 "{!r}".format(dimred))

        # Scaling
        with_mean = not config["sparse"]  # center data only if dense matrix
        scaler = StandardScaler(with_mean=with_mean) if config["scaler"] else None

        # Classifier
        try:
            classifier = _classifiers[config["classifier"]]
        except KeyError:
            raise ValueError("Unknown classification algorithm "
                             "{!r}".format(config["classifier"]))
        classifier = classifier(**config["classifier_args"])

        features = self.parse_features(config["features"])

        steps = [
            ('vectorizer', Vectorizer(features, sparse=config["sparse"])),
            ('feature_selection', selector),
            ('scaler', scaler),
            ('dimensionality_reduction', dimred),
            ('classifier', classifier)
        ]
        steps = [(name, step) for name, step in steps if step is not None]
        p = Pipeline(steps)
        self._classifier = classifier
        self.predictor = p

    def parse_features(self, feature_names):
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

    def fit(self, data):
        X = []
        y = []
        for evidence, score in data.items():
            X.append(evidence)
            y.append(int(score))
            assert y[-1] in (0, 1, -1)
        self.predictor.fit(X, y)

    def predict_proba(self, evidences):
        """
        Returns a list with the probabilities of the evidences being classified
        as ``True``.
        """
        assert sorted(self._classifier.classes_) == [0, 1]
        true_index = list(self._classifier.classes_).index(True)
        ps = self.predictor.predict_proba(evidences)
        return ps[:, true_index]

    def predict(self, evidences):
        return self.predictor.predict(evidences)

    def decision_function(self, evidences):
        # SVM predictors have decision_function which is recommended instead of
        # predict_proba, but it's not very standard.
        # Probably will raise AttributeError with other classifiers.
        result = self.predictor.decision_function(evidences).ravel()
        assert len(result) == len(evidences)
        # result is an array of 1-element arrays. Let's return the expected
        return result


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


class BagOfVerbStems(BaseBagOfVerbs):

    def name(self):
        return u'<BagOfVerbStems, in-between=%s>' % self.in_between

    def __init__(self, in_between=False):
        self.in_between = in_between
        self.do = LancasterStemmer().stem


class BagOfVerbLemmas(BaseBagOfVerbs):
    def name(self):
        return u'<BagOfVerbLemmas, in-between=%s>' % self.in_between

    def __init__(self, in_between=False):
        self.in_between = in_between
        self.wn = WordNetLemmatizer()

    def do(self, token):
        return str(self.wn.lemmatize(token.lower(), 'v'))


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


class ColumnFilter(object):
    def __init__(self, min_freq=0):
        self.m = min_freq

    def fit(self, X, y=None):
        freq = X.sum(axis=0)
        if issparse(X):
            # freq is a matrix with shape (1, 5), make it array with shape (5,)
            freq = array(freq)[0]
        self.mask = freq >= self.m
        if not self.mask.any():
            raise MoreSamplesNeededException("ColumnFilter eliminates all columns!")
        self.mapping = array([i for i, b in enumerate(self.mask) if b])
        return self

    def transform(self, X):
        return X[:, self.mask]

    def column_map(self, i):
        """Returns the input column corresonding to the i-th output column.
        """
        return self.mapping[i]
