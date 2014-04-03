from sklearn.tree import DecisionTreeRegressor


def FactExtractorFactory():
    """Instantiates a classifier ready to be fit"""
    # For now, just return something
    return DecisionTreeRegressor()
