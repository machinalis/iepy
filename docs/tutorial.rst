From 0 to IEPY
==============

In this tutorial we will guide you through the steps to create your first
Information Extraction application with IEPY.
Be sure you have a working :doc:`installation <installation>`.

IEPY internally uses `Django <https://www.djangoproject.com/>`_ to define the database models,
and to provide a web interface. You'll see some components of Django around the project, such as the
configuration file (with the database definition) and the ``manage.py`` utility. If you're familiar
with Django, you will move faster in some of the steps.


0 - Creating an instance of IEPY
--------------------------------

To work with IEPY, you'll have to create an *instance*.
This is going to be where the configuration, database and some binary files are stored.
To create a new instance you have to run:

.. code-block:: bash

    iepy --create <project_name>

Where *<project_name>* is something that you choose.
This command will ask you a few things such as database name, its username and its password.
When that's done, you'll have an instance in a folder with the name that you chose.

Read more about the instantiation process :doc:`here <instantiation>`.


1 - Loading the database
------------------------

The way we load the data into the database is importing it from a *csv* file. You can use the script **csv_to_iepy**
provided in your application folder to do it.


.. code-block:: bash

    python bin/csv_to_iepy.py data.csv

This will load **data.csv** into the database, from which the data will subsequently be accessed.

Learn more about the required CSV file format `here <instantiation.html#csv-importer>`_.


.. note::

    You might also provide a *gziped csv file.*


2 - Pre-processing the data
---------------------------

Once you have your database with the documents you want to analyze, you have to
run them through the pre-processing pipeline to generate all the information needed by IEPY's core.

The pre-processing pipeline runs a series of steps such as 
text tokenization, sentence splitting, lemmatization, part-of-speech tagging,
and named entity recognition

:doc:`Read more about the pre-processing pipeline here. <preprocess>`

Your IEPY application comes with code to run all the pre-processing steps.
You can run it by doing:

.. code-block:: bash

    python bin/preprocess.py

This *will* take a while, especially if you have a lot of data.



3 - Open the web interface
--------------------------

To help you control IEPY, you have a web user interface.
Here you can manage your database objects and label the information
that the active learning core will need.

To access the web UI, you must run the web server. Don't worry, you have everything
that you need on your instance folder and it's as simple as running:

.. code-block:: bash

    python bin/manage.py runserver

Leave that process running, and open up a browser at `http://127.0.0.1:8000 <http://127.0.0.1:8000>`_ to view
the user interface home page.

Now it's time for you to *create a relation definition*. Use the web interface to create the relation that you
are going to be using.

IEPY
----

Now, you're ready to run either the :doc:`active learning core <active_learning_tutorial>`
or the :doc:`rule based core <rules_tutorial>`.


Constructing a reference corpus
-------------------------------

To test information extraction performance, IEPY provides a tool for labeling the entire corpus "by hand"
and the check the performance experimenting with that data.

If you would like to create a labeled corpus to test the performance or for other purposes, take a look at
the :doc:`corpus labeling tool <corpus_labeling>`
