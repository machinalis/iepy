How to Hack
===========

There are several places where you can incorporate your own ideas and needs into IEPY.

On :doc:`preprocess <preprocess>` section was already mentioned that you can customize how the corpus is created.

Another place where you can do whatever fit best your needs is on the definition
of the *extraction classifier* for the *active learning* running mode.

As the simplest example of doing this, check the following example.
First, define your own custom classifier, like this:

.. code-block:: python

    from sklearn.linear_model import SGDClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.feature_extraction.text import CountVectorizer


    class MyOwnRelationClassifier:
        def fit(self, X, y):
            vectorizer = CountVectorizer(
                preprocessor=lambda evidence: evidence.segment.text)
            classifier = SGDClassifier()
            self.pipeline = make_pipeline(vectorizer, classifier)
            self.pipeline.fit(X, y)
            return self

        def predict(self, X):
            return self.pipeline.predict(X)

        def decision_function(self, X):
            return self.pipeline.decision_function(X)


and later, in iepy_runner.py of your IEPY instance, in the **ActiveLearningCore** creation,
provide it as a configuration parameter like this


.. code-block:: python

    iextractor = ActiveLearningCore(relation, labeled_evidences,
                                    performance_tradeoff=tuning_mode,
                                    extractor_config={},
                                    extractor=MyOwnRelationClassifier
                                   )
