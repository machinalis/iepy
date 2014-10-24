From 0 to IEPY
==============

In this tutorial we will guide you through the steps to create your first
Information Extraction application with IEPY.
Be sure you have a working :doc:`installation <installation>`.


0 - Creating an instance of IEPY
--------------------------------

To work with IEPY, you'll have to create an *instance*.
This is going to be where the configuration, database and some binary files are stored.
To create a new instance you have to run:

.. code-block:: bash

    iepy <project_name>

Where *<project_name>* is something that you choose.
This command will ask you a phew things such as database name, its username and its password.
When that's done, you'll have a folder with the name that you choose and the following structure:

.. code-block:: bash

    yourproject
    ├── yourproject_settings.py
    ├── yourproject.sqlite
    ├── bin
    │   ├── csv_to_iepy.py
    │   ├── iepy_rules_runner.py
    │   ├── iepy_runner.py
    │   ├── manage.py
    │   └── preprocess.py
    ├── extractor_config.json
    └── rules.py

Note that instead of *yourproject* you'll have your own project name there.

Lets see why each one of this files is there:

    * **yourproject_settings.py** is a configuration file where you can change the database
      settings and all the web interface related settings. This file has a `django settings <https://docs.djangoproject.com/en/1.7/ref/settings/>`_
      file format.
    * **yourproject.sqlite** is the default database in an sqlite format. This has no data yet, you'll have to fill it with your own data.
    * **extractor_config.json** has all the configuration of the active learning core in a *json* format.
    * **rules.py** is the place where you'll write the rules if you want to use the rule based system.
    * **bin**
        * **csv_to_iepy.py** is a tool to import data from a csv file into the database.
        * **iepy_rules_runner.py** will run the core using the rule based system.
        * **iepy_runner.py** will run the core using the active learning core.
        * **manage.py** is a `django manage file <https://docs.djangoproject.com/en/1.7/ref/django-admin/>`_ to control the web user interface.
        * **preprocess** will preprocess the data loaded in your database.


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
    * Text segmentation into fact-finding relevant parts.

Your IEPY application comes with code to run all the preprocessing steps. 

You can run it by doing:

.. code-blocK:: bash

    python bin/preprocess.py

This *will* take a while, specially if you have a lot of data.

.. note::

    To customize this process, take a look at the :doc:`how to hack <how_to_hack>` documentation.


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

There you can use the interface to create a relation definition.

4 - Run the core
----------------

Alright, you're ready to run either the *active learning* core or the *rule based core*.
The rule based core requires some more work so if you're planning to use it take a look
at that on the :doc:`rules tutorial <rules_tutorial>`.

The active learning core can be run doing:

.. code-blocK:: bash

    python bin/iepy_runner.py <relation_name>

This will run until it needs you to label some of the evidences. At this point, what you
need to do is go to the web interface that you ran on the previous step, and there you
can label some evidences.

When you consider that is enough, go to the prompt that the iepy runner presented you,
and continue the execution by typing **run**.

That will cycle again and repeat the process.
