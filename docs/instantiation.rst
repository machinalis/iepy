Instantiation
=============

Here will explain in detail what does a instantiation contains and what is it for.

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


Lets see why each one of this files is there:


Settings file
.............

settings.py is a configuration file where you can change the database settings and all the web interface related settings.
This file has a `django settings <https://docs.djangoproject.com/en/1.7/ref/settings/>`_ file format.

Database
........

When you create an instance, a database is created by default.
This is a database with sqlite format. It has no data yet, since you'll have to fill it with your own data.

When working with big datasets, it's recommended to use some other database engine instead of *sqlite*.
To change the database engine, change the settings file on the section where it says `DATABASES`:

::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'database_name_you_picked.sqlite',
        }
    }

You can change the engine to use, for example, PostgreSQL like this:

::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': 'your_database_name',
        }
    }

Take a look at the `django database configuration documentation <https://docs.djangoproject.com/en/dev/ref/settings/#databases>`_ for more detail.

.. note::

    Each time you change your database (either the db-engine, or the db name) you will have
    to instruct *django* to create all the tables in there, like this:

    .. code-block:: bash

        python bin/manage.py migrate


Active learning configuration
.............................

``extractor_config.json`` has all the configuration of the active learning core in a *json* format.

Rules definition
................

If you decide to use the rule based core, you'll have to define all your rules in the file ``rules.py``

You can verify if your rules run correctly using ``bin/rules_verifier.py``.
Read more about it `here <rules_tutorial.html#verifying-your-rules>`__.

CSV importer
............

On the ``bin`` folder, you'll find a tool to import data from csv files. This is the script ``csv_to_iepy.py``.
Your csv data has to be on the following format:

::

    <document_id>, <document_text>

Preprocess
..........

To preprocess your data, you will use the  ``bin/preprocess.py``. Read more about it :doc:`here <preprocess>`

Runners
.......

On the ``bin`` folder, you have scripts to run either the active learning core (``iepy_runner.py``) or the
rule based core (``iepy_rules_runner.py``)

Web UI management
.................

For the web server management, you have the ``bin/manage.py`` script. This is a `django manage file <https://docs.djangoproject.com/en/1.7/ref/django-admin/>`_
and with it you can start up your server.


Instance Upgrade
----------------

From time to time, small changes on the iepy internals will need some *upgrade* of the existent iepy instances.

The upgrade process will apply the needed changes to the instance-folder structure.

In the case you made local changes, the tool will preserve a copy of your changes so you can merge by hand on the conflicting areas.

For upgrading a iepy instance, simply run the following command

    .. code-block:: bash

        iepy --upgrade <instance path>

.. note::

    On any instance you can know which is the iepy-version of it by looking at the settings file.
