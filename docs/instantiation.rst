Instantiation
=============

Here, we'll explain in detail what an instantiation contains and what it does.

Folder structure
----------------

The folder structure of an iepy instance is the following:

.. code-block:: bash

    ├── __init__.py
    ├── settings.py
    ├── database_name_you_picked.sqlite
    ├── bin
    │   ├── csv_to_iepy.py
    │   ├── iepy_rules_runner.py
    │   ├── iepy_runner.py
    │   ├── manage.py
    │   ├── preprocess.py
    │   └── rules_verifier.py
    ├── extractor_config.json
    └── rules.py


Let's see why each one of those files is there:


Settings file
.............

settings.py is a configuration file where you can change the database settings and all the web interface related settings.
This file has a `django settings <https://docs.djangoproject.com/en/1.7/ref/settings/>`_ file format.

Database
........

When you create an instance, a *sqlite* database is created by default.
It has no data yet, since you'll have to fill it with your own data.

When working with big datasets, it's recommended to use some database engine other than *sqlite*.
To change the database engine, change the `DATABASES` section of the settings file:

::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'database_name_you_picked.sqlite',
        }
    }

For example, you can use PostgreSQL like this:

::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'your_database_name',
        }
    }

(Remember that you'll need to install ``psycopg2`` first with a simple ``pip install psycopg2``)

Take a look at the `django database configuration documentation <https://docs.djangoproject.com/en/dev/ref/settings/#databases>`_ for more detail.

.. note::

    Each time you change your database (either the engine or the name) you will have
    to instruct *django* to create all the tables in it, like this:

    .. code-block:: bash

        python bin/manage.py migrate


Active learning configuration
.............................

``extractor_config.json`` specifies the configuration of the active learning core in *json* format.

Rules definition
................

If you decide to use the rule based core, you'll have to define all your rules in the file ``rules.py``

You can verify if your rules run correctly using ``bin/rules_verifier.py``.
Read more about it `here <rules_tutorial.html#verifying-your-rules>`__.

CSV importer
............

In the ``bin`` folder, you'll find a tool to import data from CSV files. This is the script ``csv_to_iepy.py``.
Your CSV data has to be in the following format:

::

    <document_id>, <document_text>

Preprocess
..........

To preprocess your data, you will use the  ``bin/preprocess.py`` script. Read more about it :doc:`here <preprocess>`

Runners
.......

In the ``bin`` folder, you have scripts to run the active learning core (``iepy_runner.py``) or the
rule based core (``iepy_rules_runner.py``)

Web UI management
.................

For the web server management, you have the ``bin/manage.py`` script. This is a `django manage file <https://docs.djangoproject.com/en/1.7/ref/django-admin/>`_
and with it you can start up your server.


Instance Upgrade
----------------

From time to time, small changes in the iepy internals will require an *upgrade* of existing iepy instances.

The upgrade process will apply the needed changes to the instance-folder structure.

If you made local changes, the tool will preserve a copy of your changes so you can merge the conflicting areas by hand.

To upgrade an iepy instance, simply run the following command

    .. code-block:: bash

        iepy --upgrade <instance path>

.. note::

    Look at the settings file to find the version of any iepy instance.
