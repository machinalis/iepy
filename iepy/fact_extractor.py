from featureforge.vectorizer import Vectorizer
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor


def FactExtractorFactory(data, relation):
    """Instantiates and trains a classifier."""
    # Simplistic Pseudocode. For now, just return some dummy classifier
    p = Pipeline([
        ('vectorizer', get_vectorizer(relation)),
        ('classifier', DecisionTreeRegressor())
    ])
    X, y = zip(*data.items())
    p.fit_transform(X, y)
    return p


def get_vectorizer(relation):
    # Pseudocode. Example Feature.
    def _relation_name_in_segment(relation_name, evidence):
        return relation_name.lower() in map(lambda x: x.lower(), evidence.segment.tokens)
    return Vectorizer([lambda e: _relation_name_in_segment(relation, e)])
