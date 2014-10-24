from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline, make_union
from featureforge.vectorizer import Vectorizer

from iepy.extraction.features import parse_features


_valid_classifiers = {
    "sgd": SGDClassifier,
    "knn": KNeighborsClassifier,
    "svc": SVC,
    "randomforest": RandomForestClassifier,
    "adaboost": AdaBoostClassifier,
}


_configuration_options = """
    classifier
    classifier_args
    sparse_features
    dense_features
""".split()


class RelationExtractionClassifier:
    def __init__(self, **config):
        # Validate options are present
        for option in _configuration_options:
            if option not in config:
                raise ValueError("Missing configuration "
                                 "option {!r}".format(option))

        # Feature extraction
        sparse_features = parse_features(config["sparse_features"])
        densifier = make_pipeline(Vectorizer(sparse_features, sparse=True),
                                  ClassifierAsFeature())
        dense_features = parse_features(config["dense_features"])
        vectorization = make_union(densifier,
                                   Vectorizer(dense_features, sparse=False))

        # Classifier
        try:
            classifier = _valid_classifiers[config["classifier"]]
        except KeyError:
            raise ValueError("Unknown classification algorithm "
                             "{!r}".format(config["classifier"]))
        classifier = classifier(**config["classifier_args"])

        self.pipeline = make_pipeline(vectorization, StandardScaler())
        self.classifier = classifier

    def fit(self, X, y):
        X = self.pipeline.fit_transform(X, y)
        self.classifier.fit(X, y)
        return self

    def _chew(self, evidences):
        return self.pipeline.transform(evidences)

    def _predict(self, X):
        return self.classifier.predict(X)

    def _rank(self, X):
        return self.classifier.decision_function(X).ravel()

    def predict(self, evidences):
        return self._predict(self._chew(evidences))

    def decision_function(self, evidences):
        return self._rank(self._chew(evidences))


class ClassifierAsFeature:
    """
    A transformation that esentially implements a form of dimensionality
    reduction.
    This class uses (by default) a fast SGDClassifier configured like a linear
    SVM to produce a feature that is the decision function of the classifier.
    It's useful to reduce the dimension of bag-of-words feature-set into a
    feature that's denser in information.
    """
    def __init__(self, classifier=None):
        if classifier is None:
            classifier = SGDClassifier()
        self.classifier = classifier

    def fit(self, X, y):
        """
        `X` is expected to be an array-like or a sparse matrix.
        `y` is expected to be an array-like containing the classes to learn.
        """
        self.classifier.fit(X, y)
        return self

    def transform(self, X, y=None):
        """
        `X` is expected to be an array-like or a sparse matrix.
        It returns a dense matrix of shape (n_samples, 1).
        """
        return self.classifier.decision_function(X).reshape(-1, 1)
