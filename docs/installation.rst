==================
IEPY installation
==================

IEPY runs on *python 3*, and it's fully tested with version *3.4*.
This installation notes assume that you have a fresh just installed *ubuntu 14.04*.
If you are running this installation on a different platform, some details
or software versions may be slightly different.

Because of some of it's dependencies, IEPY installation it's not a single
pip install, but it's actually not that hard.

Outline:
    - install some system packages
    - install iepy itself
    - download 3rd party binaries


System software needed
----------------------

You need to install the following packages:

.. code-block:: bash

    sudo apt-get install build-essential python3-dev liblapack-dev libatlas-dev gfortran openjdk-7-jre

They are needed for python scipy & numpy installation, and for running
some java processes. If anything fails during the IEPY installation below,
don't hesitate on checking fully installation notes for
SciPy `here <http://www.scipy.org/install.html>`_


Install IEPY package
--------------------

1. `Virtualenv creation`_

2. Install IEPY itself

.. code-block:: bash

    pip install iepy

3. Configure Java home

This step is only required for python 3 installations.
    Make sure of having defined the environment variable JAVAHOME=/usr/bin/java (or the path where java was installed)
    Make sure of making somehow persistent this configuration.

Download the third party data and tools
---------------------------------------

You should have now a command named "*iepy*", use it like this for getting some needed
binaries.

.. code-block:: bash

    iepy --download-third-party-data


Virtualenv creation
-------------------

For organization sake, its strongly recommended to make all the IEPY
installation inside a virtual python environment.

We shouldn't be explaining how to create it here, so we wont.
There is way better documentation
`here <https://docs.python.org/3.4/library/venv.html>`_
for python 3.4.

Just make sure of have it created and activated while following the
IEPY installation instructions.
Some small notes before leading you to the good documentation:

 - If you are working with python3.3 (or 3.4 but with the buggy ubuntu/debian release),
   be warn that you will need to install *pip* by hand,
   as explained `here <http://pip.readthedocs.org/en/latest/installing.html#install-pip>`_
 - Alternatively, create your virtualenv with `virtualenvwrapper <http://virtualenvwrapper.readthedocs.org/en/latest/install.html#basic-installation>`_


Creating an instance of IEPY
----------------------------

Once you're done with the installation, to actually make use of iepy you'll have to create an *instance*.
This is going to be where the configuration, database and some binary files are stored.

To create a new instance you have to run:

.. code-block:: bash

    iepy <project_name>

Where *<project_name>* is something that you choose.
This command will ask you a phew things such as database name, username and password for that database.
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
      file format. If you desire to change your database, this is the place where you need to edit.
    * **yourproject.sqlite** is the database in an sqlite format.
    * **extractor_config.json** has all the configuration of the active learning core in a *json* format.
    * **rules.py** is the place where you'll write the rules if you want to use the rule based system.
    * **bin**
        * **csv_to_iepy.py** is a tool to import data from a csv file into the database.
        * **iepy_rules_runner.py** will run the core using the rule based system.
        * **iepy_runner.py** will run the core using the active learning core.
        * **manage.py** is a `django manage file <https://docs.djangoproject.com/en/1.7/ref/django-admin/>`_ to control the web user interface.
        * **preprocess** will preprocess the data loaded in your database.
