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

Execute the IEPY bootstrap pipeline runner with

::

  $ python scripts/iepy_runner.py <dbname> <seeds_file> <output_file>


where ``<dbname>`` is the name of the database generated in section X, 
``<seeds_file>`` is the seed facts file generated in section Y and 
``<output_file>`` is the file where IEPY will save the found facts.

On each iteration of the bootstrapping process, IEPY will look in the database 
for pieces of text that have a good chance to be evidences of facts. You will be
asked to confirm or reject each evidence.

::

  Possible answers are:
     y: Valid Evidence
     n: Not valid Evidence
     d: Discard, not sure
     run: Tired of answering for now. Run with what I gave you.
     STOP: Stop execution ASAP

When you are tired of a round of answering, type ``run`` and IEPY will complete 
one loop of bootstrapping, by learning a classifier and reclassifying the text 
fragments.

When you want to stop the entire process, type ``STOP`` and IEPY will output a 
CSV file with the found facts with references to the document parts that support
the fact.

The first five columns of the output CSV format specify the fact (as in the seed
facts input file):

::

  entity A kind, entity A name, entity B kind, entity B name, relation name

The remaining columns specify the document part in the database where the fact
can be found:

::

  document name, segment offset, entity A index, entity B index

where ``segment offset`` is the text segment offset into the document and the 
entity indexes indicate the entity positions into the segment.


Generate knowledge/reference corpus/gold standard (fully supervised)
--------------------------------------------------------------------

Label data using iepy/generate_reference_corpus.py.


Train and test the classfiers (fully supervised)
------------------------------------------------

Use scripts/cross_validate.py.


Profit! Or not
--------------

How?

