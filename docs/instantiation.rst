Instantiation
=============

Here will explain in detail what does a instantiation contains and what is it for.

Folder structure
----------------

The folder structure of an iepy instance is the following:

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


Settings file
.............

yourproject_settings.py is a configuration file where you can change the database
settings and all the web interface related settings. 

This file has a `django settings <https://docs.djangoproject.com/en/1.7/ref/settings/>`_ file format.

Database
........

When you create an instance, a database is created by default on the file **yourproject.sqlite**.
This is a database with  sqlite format.  This has no data yet, you'll have to fill it with your own data.

To change the database engine, change the settings file on the section where it says `DATABASES`:

::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'yourproject.sqlite',
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

Active learning configuration
.............................

**extractor_config.json** has all the configuration of the active learning core in a *json* format.

Rules definition
................

If you decide to use the rule based core, you'll have to define all your rules in the file **rules.py**

CSV importer
............

On the **bin** folder, you'll find a tool to import data from csv files. This is the script **csv_to_iepy.py**.
Your csv data has to be on the following format:

::
    
    <document_id>, <document_text>

Preprocess
..........

To preprocess your data, you will use the  **preprocess.py** script that is located on the **bin** folder.

Runners
.......

On the bin folder, you have scripts to run either the active learning core (**iepy_runner.py**) or the
rule based core (**iepy_rules_runner.py**)

Web UI managment
................

For the web server managment, you have the **manage.py** script. This is a `django manage file <https://docs.djangoproject.com/en/1.7/ref/django-admin/>`_ 
and with it you can start up your server
