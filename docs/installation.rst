==================
IEPY installation
==================

IEPY runs on *python 3*, and it's fully tested with version *3.4*.
These installation notes assume that you have a fresh installation of *Ubuntu 14.04*.
If you are installing IEPY on a different platform, some details
or software versions may be slightly different.

Because of some of its dependencies, IEPY installation is not a single
pip install, but it's actually not that hard.

Outline:
    - install some system packages
    - install iepy itself
    - download 3rd party binaries


System software needed
----------------------

You need to install the following packages:

.. code-block:: bash

    sudo apt-get install build-essential python3-dev liblapack-dev libatlas-dev gfortran

They are needed for python Numpy installation. Once this is done, install numpy by doing:

.. code-block:: bash

    pip install numpy


And later, for been able to run some java processes:

.. code-block:: bash

    sudo apt-get install openjdk-7-jre

.. note::

    Instead of openjdk-7-jre you can use any other java (version 1.6 or higher) you
    may have.

    **Java 1.8** will allow you to use the **newest preprocess models**.


Install IEPY package
--------------------

1. :doc:`Create a Virtualenv <virtualenv>`

2. Install IEPY itself

.. code-block:: bash

    pip install iepy

3. Configure java & NLTK

    In order to preprocess documents, set the
    environment variable JAVAHOME=/usr/bin/java (or the path where java was installed)
    To make this configuration persistent, add it to your shell rc file.

Download the third party data and tools
---------------------------------------

You should have now a command named "*iepy*". Use it like this to get some required
binaries.

.. code-block:: bash

    iepy --download-third-party-data

.. note::

    If the java binary pointed by your JAVAHOME is 1.8, newest preprocess models will
    be acquired and used.
