==================
Language support
==================

By default IEPY will use English models, but it's also able to work with different
languages.

The preprocess machinery that's provided by default (Stanford Core NLP) has support
for some other language, so, check their models and documentation in case you need this.

.. note::

    The main goal until now was to architecture IEPY to allow different languages.
    Right now, the only fully supported languages are English and Spanish. If you need
    something else, do not hesitate in contacting us.


Language Installation and Models
--------------------------------

The language models used by IEPY (the information used during preprocessing phase)
are stored on your IEPY installation. Several models for different languages can be
installed on the same installation.

In order to download Spanish models you should run

.. code-block:: bash

    iepy --download-third-party-data --lang=es

.. note::

    Check Stanford Core NLP documentation and files to download for more language packages.


Language Definition and Instances
---------------------------------

Every IEPY instance works for a single language, which is declared on the settings.py file like this:

To change the instance language, change the settings file on the section where it says `IEPY_VERSION`:

::

    IEPY_VERSION = 'en'


For creating an IEPY instance for a different language, you should run

.. code-block:: bash

    iepy --create --lang=es <folder_path>
