Application Tutorial
====================

To be written:

* Talk about the problem definition: Pick the data, the entities and the relations.
* Feature engineering


Install
-------

Follow the installation instructions.


Create the database with your data
----------------------------------

Do something like what is done with the script tvseries/scripts/wikia_to_iepy.


Preprocess the database
-----------------------

Build and run the preprocessing pipeline (something like 
tvseries/scripts/preprocess.py).

Download required third party data and code for the pipeline:

* Punkt tokenizer
* Stanford POS tagger
* Stanford Named Entity Recognizer (NER)
* Freebase data for the desired entities

If the data is not raw text, a first step in the pipeline is required to convert
the data to raw text (like media_wiki_to_txt in tvseries/scripts/preprocess.py).


Generate the seed facts (semi-supervised)
-----------------------------------------

Label some data using iepy/generate_seeds.py.


Run the bootstrapping pipeline, and be the Human in the Loop (semi-supervised)
------------------------------------------------------------------------------

Use scripts/iepy_runner.py.


Generate knowledge/reference corpus/gold standard (fully supervised)
--------------------------------------------------------------------

Label data using iepy/generate_reference_corpus.py.


Train and test the classfiers (fully supervised)
------------------------------------------------

Use scripts/cross_validate.py.


Profit! Or not
--------------

How?

