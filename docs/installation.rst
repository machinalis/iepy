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

    sudo apt-get install python3-dev liblapack-dev libatlas-dev gfortran openjdk-7-jre

They are needed for python scipy & numpy installation, and for running some java processes.


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

You should have now a command named "*iepy*"

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
