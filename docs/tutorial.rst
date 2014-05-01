====================
Application Tutorial
====================

In this tutorial we will guide you through the steps to create your first
Information Extraction application with IEPY.
Be sure you have a working `installation <https://github.com/machinalis/iepy/blob/develop/docs/installation.rst>`_ of IEPY.



Get Started
===========


Define your Problem
-------------------

Information Extraction is about finding structured information in unstructured
documents. IEPY structures the information into predefined kinds of entities
and relations.

So, the first thing you have to do is to define which kinds of entities and
relations your application is going to find.
For instance, you may want to identify the entities of kind *person* and
*location* with the relation *was born in* or, like in our example, the entities
*disease* and *symptom* with the relation *causes*.

IEPY comes with built-in support for entity recognition of kinds *location*,
*person* and  *organization*, but it can be customized for other entity kinds.


Start a IEPY Application
------------------------

Pick a name you like for your IEPY application and run the IEPY application
creation script. For instance, to create an application with name ``myapp``, run:

.. code-block:: bash

    python scripts/startapp.py myapp

This script will create a directory named ``myapp`` ready to accommodate your
application. It will also create a couple of helper scripts that will be
described in the following sections:

::

    myapp/scripts/createdb.py
    myapp/scripts/preprocess.py


Create the IEPY Documents Database
----------------------------------

IEPY needs to have your input documents in a `MongoDB <https://www.mongodb.org/>`_ 
database. To help you do this, your IEPY application comes with the script
``createdb.py``. This script loads your database with "toy" documents, so you
have to edit it in order to make it load your actual documents.

For each document, all you have to provide is an identifier  (which must be a
unique string) and the document text.
Your documents are probably stored somewhere outside a IEPY database, so you
will need code to convert and import them.
This code will depend heavily on the format and storage of your input data,
but it will always have to write into the IEPY database.

Any script that needs to create documents in the IEPY database should do the
following::

    from iepy.db import connect, DocumentManager

    connect('database_name')
    docs = DocumentManager()

where ``'database_name'`` is any valid MongoDB database name.
The code above connects (and creates if needed) the specified database, and
creates a “Document Manager”, which is a utility object for operation on
IEPY documents stored in the database. The database operations you need to
do will be methods of ``docs``.
Creating a document consists in making a function call like this::

    docs.create_document(
        identifier="Moby Dick - Chapter I"
        text="""
        Call me Ishmael. Some years ago—never mind how long precisely—having
        little or no money in my purse, and nothing particular to interest me
        on shore, I thought I would sail about a little and see the watery part
        of the world. It is a way I have of driving off the spleen and
        regulating the circulation. ...
        """)

In a more typical case, if you have a directory called ``Documents`` full of text
files, your import script might look like this::

    documents = os.listdir("Documents")
    for d in documents:
        filename = os.path.join("Documents", d)
        with open(filename) as f:
            docs.create_document(identifier=d, text=f.read())

The ``create_document`` method allows you to add any additional metadata you
want by passing a dictionary as a ``metadata`` argument. This metadata can be
used in later preprocessing steps, or just stored in the database as reference
information on the document. Extending the example above, if you want to 
save the original filename and the import time, you could change the call
to ``create_document`` as follows::

    docs.create_document(
        identifier=d,
        text=f.read(),
        metadata={
            'source_filename': filename,
            'import_time': str(datetime.datetime.now())
        })

The keys for the dictionary are essentially free-form. At this moment, there
are no values with a predefined semantic, so you may choose whatever you
want for your application.


Handling different input formats
--------------------------------

Sometimes, your input documents are in some non-text format that you want to
preserve (for example HTML, wiki markup, etc.), instead of converting on the
fly while importing the data. This may be useful to link back results you get
later to the original document.

The best way to do this is to import the raw data and defer data conversion
to a later step (see preprocessing below). If you want to do this you can
add the original text as metadata, and leave the text empty, like this::

    docs.create_document(
        identifier=d, text='',
        metadata={'raw_data': non_text_data}
    )

In this case, the first step in your preprocessing pipeline should be a
conversion function that gets the data from ``document.metadata['raw_data']``
and sets ``document.text``.

The IEPY application you created comes with code prepared to do this.
Also, to see a working example you can refer to our demo application.
For more details proceed to the next section.


Preprocess the Documents
========================

Once you have your database with the documents you want to analyze, you have to
run the preprocessing pipeline to generate all the information needed by IEPY's
core.

The preprocessing pipeline runs the following steps:

1) Text tokenization and segmentation into sentences.
2) Part-Of-Speech (POS) tagging.
3) Named Entity Recogntion (NER).
4) Text segmentation into fact-finding relevant parts.

Your IEPY application comes with code to run all the preprocessing steps with
the script ``myapp/scripts/preprocess.py``.
It uses third party software and data, such as the `punkt tokenizer
<http://www.nltk.org/api/nltk.tokenize.html>`_, the `Stanford POS tagger
<http://nlp.stanford.edu/software/tagger.shtml>`_ and the `Stanford Named Entity
Recognizer <http://nlp.stanford.edu/software/CRF-NER.shtml>`_.

However, you may need to add some custom code, specially in two particular cases:

- The documents are not in plain text: If your documents are not in plain text
  format and you didn't convert them to plain text when you created the database,
  you will have to add an additional processing step at the beggining.
  IEPY provides you with a stub (``extract_plain_text``) so you can insert your
  code to convert the documents to plain text.
  You can find a working example of this in the preprocessing script for our
  demo application (``examples/tvseries/scripts/preprocess.py``).
- You want to work with custom entity kinds: The provided NER only recognizes
  locations, persons and organizations. You can either program your own NER (or a
  wrapper for an existing NER) and use it in the pipeline, or you can use the
  Literal NER described in the following subsection.


Use the Literal Named Entity Recognizer
---------------------------------------

A quick option to have a very simple baseline NER for any entity kind you want
is to use IEPY's Literal Named Entity Recognizer.
IPEY's Literal NER reads from a text file all the possible entity instance names,
and tags all the exact matches of these names in the documents.

For instance, to add NER for diseases and symptoms for your IEPY application,
edit ``myapp/scripts/preprocess.py`` as follows:

.. code-block:: python

  CUSTOM_ENTITIES = ['DISEASE', 'SYMPTOM']
  CUSTOM_ENTITIES_FILES = ['myapp/disease.txt', 'myapp/symptom.txt']


Then, write all the diseases and symptoms you know in the files
``myapp/disease.txt`` and ``myapp/symptom.txt``, or, much better, download them
from Freebase as shown in next section.


Download Entity Instances from Freebase
---------------------------------------

You will probably be able to identify the entity kinds you are interested in
with types in the `Freebase <http://www.freebase.com/>`_ ontology.
If this is the case, you can order IEPY to download from Freebase the names and
aliases of all the instances of a given type, and save them into a text file
that can be used by the Literal NER.

For instance, to download all the diseases and symptoms known by Freebase, run

.. code-block:: bash

    python scripts/download_freebase_type.py /medicine/disease myapp/disease.txt --aliases --to-lower
    python scripts/download_freebase_type.py /medicine/symptom myapp/symptom.txt --aliases --to-lower


Run the Pipeline
----------------

Once you are done preparing the preprocessing pipeline, you can run it:

.. code-block:: bash

    python myapp/scripts/preprocess.py <dbname>

The preprocessing pipeline runner will run all the steps in the pipeline and
your documents database will be ready for IEPY's core.


Generate the Seed Facts
=======================

IEPY takes as input a small set of seed facts that you have to provide to it.
The seed facts are positive examples of the relations you want IEPY to look for.

You can either write the seed facts manually, or use IEPY's seed generation tool.
In any case, the seeds facts are written in a CSV file with the following format::

  entity A kind, entity A name, entity B kind, entity B name, relation name

For instance, if you have diseases and symptoms and you want to find which
disease causes which symptom, you can provide a seed fact such as

::

  disease,botulism,symptom,paralysis,CAUSES


IEPY can help you generating the seed facts by looking in the document and
asking you questions:

.. code-block:: bash

    python scripts/generate_seeds.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename>

For instance, to generate seeds for the CAUSES relation between diseases and
symptoms, run

.. code-block:: bash

    python scripts/generate_seeds.py <dbname> CAUSES disease symptom causes_seeds.csv


Run IEPY
========

Execute the IEPY bootstrap pipeline runner with

.. code-block:: bash

    python scripts/iepy_runner.py <dbname> <seeds_file> <output_file>

where ``<seeds_file>`` is the seed facts file generated in the previous section,
and ``<output_file>`` is the file where IEPY will save the found facts.


Help IEPY a Bit
---------------

On each iteration of the bootstrapping process, IEPY will look in the database
for pieces of text that have a good chance to be evidences of facts. You will be
asked to confirm or reject each evidence. The possible answers are:

- y: Valid Evidence.
- n: Not valid Evidence.
- d: Discard, not sure.
- run: Tired of answering for now. Run with what I gave you.
- STOP: Stop execution ASAP

When you are tired of a round of answering, type ``run`` and IEPY will complete
one loop of bootstrapping, by learning a classifier and reclassifying the text
fragments.

When you want to stop the entire process, type ``STOP`` and IEPY will finish
working and output the results.


Profit! Or not :)
=================

When finished, IEPY outputs a CSV file with the found facts along with
references to the document parts that support them. The first five columns of
the output CSV format specify the fact (as in the seed facts input file)::

  entity A kind, entity A name, entity B kind, entity B name, relation name

The remaining columns specify the document part in the database where the fact
can be found::

  document name, segment offset, entity A index, entity B index

where ``segment offset`` is the text segment offset into the document and the
entity indexes indicate the entity positions into the segment. These indexes are
all internal to the database and depends on how the documents are preprocessed.

For a human-readable version of the CSV output, you can use IEPY's results
pretty printer:

.. code-block:: bash

    python scripts/print_results.py <dbname> <csv_file>

This script will output all the facts in the CSV file with their respective 
evidences.

