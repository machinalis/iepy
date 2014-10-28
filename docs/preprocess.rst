About the Pre-Process
=====================

The preprocessing adds the metadata that iepy needs to detect the relations, this includes:

    * Text tokenization and segmentation into sentences.
    * Part-Of-Speech (POS) tagging.
    * Named Entity Recogntion (NER).

We're currently running all this steps using the `Stanford CoreNLP <http://nlp.stanford.edu/software/corenlp.shtml>`_ tools.
This runs in a all-in-one run, but every step can be :ref:`modified to use a custom version <customize>` that adjust your needs.


About the Segmentation and tokenization
---------------------------------------

IEPY works on a segment level, this means that will try to find if a relation is present within a segment of text. The
pre-process is the responsible for spliting the documents into segments.

Each one of these segments are divided into tokens. 

Part of speech tagging
----------------------

Each token is augmented with metadata about its part of speech such as noun, verb, adjective and other grammatical tags.
Along the token itself, this is used by the NER to detect an entity occurrence.

The one used by default it's the `Stanford Log-linear Part-Of-Speech Tagger <http://nlp.stanford.edu/software/tagger.shtml>`_

Named Entity Recogntion
-----------------------

To find a relation between entities one must first recognize these entities in the text. An automatic NER is used to find
ocurrences of an entity in the text.

The default process is the `Stanford Named Entity Recognizer <http://nlp.stanford.edu/software/CRF-NER.shtml>`_ and locates
entity ocurrences of the following kinds:

    * Location
    * Person
    * Organization

This process can be customized to find entities of kinds defined by you.


.. _customize:

How to customize
----------------

On your own IEPY instances, there's a file called ``preprocess.py`` located in the ``bin`` folder. There you'll find
that the default is simply run the stanford preprocess. This can be changed to run a serious of steps defined by you

For example, take this pseudo-code to guide you:

.. code-block:: python

    pipeline = PreProcessPipeline([
        CustomTokenizer(),
        CustomSegmenter(),
        CustomPOSTagger(),
        CustomNER(),
    ], docs)
    pipeline.process_everything()


.. note::

    The steps can be functions or methods that define the `__call__`. We recomend objects because generally you'll
    want to do some load up of things on the `__init__` method to avoid loading everything over and over again.

Each one of those steps will be called with each one of the documents, this means that for every step will be called
with al the documents, after finishing with that the next step will be called with each one of the documents.
