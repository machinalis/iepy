Application Tutorial
====================

To be written:

* Talk about the problem definition: Pick the data, the entities and the relations.
* Feature engineering


Start a IEPY project
--------------------

::

  $ python scripts/startapp.py myapp


Create the database with your data
----------------------------------

Do something like what is done with the script tvseries/scripts/wikia_to_iepy.


Preprocess the Documents
------------------------

Once you have your database with the documents you want to analyze, you have to
run the preprocessing pipeline to generate all the information needed by IEPY's 
core.

The preprocessing pipeline runs the following steps:

1) Text tokenization and segmentation into sentences.
2) Part-Of-Speech (POS) tagging.
3) Named Entity Recogntion (NER).
4) Text segmentation into relevant parts.

Your IEPY application comes with code to run all the steps, sometimes using
third party software and data, such as the `punkt tokenizer
<http://www.nltk.org/api/nltk.tokenize.html>`_, the `Stanford POS tagger 
<http://nlp.stanford.edu/software/tagger.shtml>`_ and the `Stanford Named Entity
Recognizer <http://nlp.stanford.edu/software/CRF-NER.shtml>`_.

However, you may want to add some custom code, specially if you want to work 
with entities other than the ones found by the Stanford NER (locations, persons 
and organizations).

...

Generate the Seed Facts
-----------------------

IEPY takes as input a small set of seed facts that you have to provide to it.
The seed facts are positive examples of the relations you want IEPY to look for.

You can either write the seed facts manually, or use IEPY's seed generation tool.
In any case, the seeds facts are written in a CSV file with the following format:

::

  entity A kind, entity A name, entity B kind, entity B name, relation name

For instance, if you have diseases and symptoms and you want to find which 
disease causes which symptom, you can provide a seed fact such as 

::

  disease,botulism,symptom,paralysis,CAUSES


IEPY can help you generating the seed facts by looking in the document and 
asking you questions.

::

  $ python scripts/generate_seeds.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename>

For instance, to generate seeds for the CAUSES relation between diseases and 
symptoms, run

::

  $ python scripts/generate_seeds.py <dbname> CAUSES disease symptom causes_seeds.csv


Run IEPY, and be the Human in the Loop
--------------------------------------

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


Profit! Or not
--------------

How?

