From 0 to IEPY
==============

In this tutorial we will guide you through the steps to create your first
Information Extraction application with IEPY.
Be sure you have a working :doc:`installation <installation>`.

IEPY internaly uses `Django <https://www.djangoproject.com/>`_ to define the database models,
and for the web interface so you'll see some components of it around the project, such as the
configuration file (with the database definition) and the ``manage.py``. If you're familirized
with it, you will move faster in some of steps.


0 - Creating an instance of IEPY
--------------------------------

To work with IEPY, you'll have to create an *instance*.
This is going to be where the configuration, database and some binary files are stored.
To create a new instance you have to run:

.. code-block:: bash

    iepy <project_name>

Where *<project_name>* is something that you choose.
This command will ask you a few things such as database name, its username and its password.
When that's done, you'll have an instance in a folder with the name that you choose
Read more about the instantiation :doc:`here <instantiation>`.


1 - Loading the database
------------------------

The way we load the data into the database is importing it from a *csv* file. You can use the script **csv_to_iepy** 
provided in your application folder to do it.


.. code-blocK:: bash

    python bin/preprocess.py data.csv

This will load **data.csv** into the database and from now on, you will work accessing
the data from there. 

.. note::

    You might also provide a *gziped csv file.*


2 - Pre-processing the data
---------------------------

Once you have your database with the documents you want to analyze, you have to
run the pre-process to generate all the information needed by IEPY's core.

The preprocessing pipeline runs the following steps:

    * Text tokenization and segmentation into sentences.
    * Part-Of-Speech (POS) tagging.
    * Named Entity Recogntion (NER).

Your IEPY application comes with code to run all the preprocessing steps. 

You can run it by doing:

.. code-blocK:: bash

    python bin/preprocess.py

This *will* take a while, specially if you have a lot of data.

:doc:`Read more about the pre-process here. <preprocess>`


3 - Open the web interface
--------------------------

To help you control IEPY, you have a web user interface.
Here you can manage your database objects as well as labeling the information
that the active learning core will need.

To access it you must get the web server. Don't worry, you have everything
that you need on your instance folder and it's as simple as running:

.. code-blocK:: bash

    python bin/manage.py runserver

And done! Leave that running and open up a browser at `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_ to get
the user interface home page.

Now it's time for you to *create a relation definition*. Use the web interface to create the relation that you
are going to be using.

IEPY
----

Alright, you're ready to run either the :doc:`active learning core <active_learning_tutorial>`
or the :doc:`rule based core <rules_tutorial>`.


Constructing a reference corpus
-------------------------------

To test the performance IEPY provides a tool to label all the corpus "by hand" and then check the performance
experimenting with that data.

If you would like to create a labeled corpus to test the performance or for other purposes, take a look at
the :doc:`corpus labeling tool <corpus_labeling>`
