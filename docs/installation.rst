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
SciPy `here <http://www.scipy.org/install.html>`__


Install IEPY package
--------------------

1. :doc:`Create a Virtualenv <virtualenv>`

2. Install IEPY itself

.. code-block:: bash

    pip install iepy

3. Configure java & NLTK

    In order to be able to run documents preprocess, it's needed to have defined an
    environment variable JAVAHOME=/usr/bin/java (or the path where java was installed)
    Make sure of making somehow persistent this configuration (your shell rc file, for example).

Download the third party data and tools
---------------------------------------

You should have now a command named "*iepy*", use it like this for getting some needed
binaries.

.. code-block:: bash

    iepy --download-third-party-data


