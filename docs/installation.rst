==================
IEPY installation
==================

IEPY runs on *python 3*, and it's fully tested with version *3.4*.
This installation notes assume that you have a just installed *ubuntu 14.04
desktop version*. Some details or software versions may be slightly different
if you are running from a different platform.

Because of it's dependencies, installation it's not a single pip install,
and requires a bit of extra work, but it's actually not that hard.

Outline:
    - install some system packages
    - install iepy itself
    - download 3rd party binaries
    - (optional) install development tools


System software needed
======================

You need to install the following packages:

.. code-block:: bash

    sudo apt-get install python3-dev liblapack-dev libatlas-dev gfortran openjdk-7-jre

They are needed for python scipy & numpy installation, and for running some java processes.


Python libraries installation
-----------------------------

1. `Virtualenv creation and initial setup`_

2. Get IEPY code

.. code-block:: bash

    git clone https://github.com/machinalis/iepy.git

3. Install IEPY and all the needed python libraries.

.. code-block:: bash

    cd <path-to-gitrepo>
    pip install .

**Warning**, if you are using pip 1.5 (will probably be the case on python3) you will have to use the extra argument *--process-dependency-links* as shown below, otherwise some packages (like nltk for python3) wont be available

.. code-block:: bash

    cd <path-to-gitrepo>
    pip install . --process-dependency-links


4. Configure Java home

This step is only required for python 3 installations.
    Make sure of having defined the environment variable JAVAHOME=/usr/bin/java (or the path where java was installed)
    Make sure of making somehow persistent this configuration.

5. Download the third party data and tools

.. code-block:: bash

    cd <path-to-gitrepo>
    python scripts/download_third_party_data.py


Installing Development tools:
=============================

If you want to contribute, or do some modifications or customizations, you will need to install some extra python packages.
So, with your virtualenv activated, please run the following (replacing *<NUMBER>* with 2 or 3, depending if you are installing IEPY for python 2.x or 3.x)

.. code-block:: bash

    cd <path-to-gitrepo>
    pip install -r docs/setup/requirements-development-py<NUMBER>.txt


Installing Example TV Series application
========================================

There's an example application, named "TV Series", located on the *examples* folder of the IEPY repository. It has it's own install document that you can find at here:

<path-to-gitrepo>/examples/tvseries/docs/setup/INSTALL.txt

Follow those instructions with your virtualenv activated.


Virtualenv creation and initial setup
=====================================

We shouldn't be explaining this, so we wont.
There is way better documentation
`here <http://virtualenv.readthedocs.org/en/latest/virtualenv.html>`_
for python 2.7 or `here <https://docs.python.org/3.3/library/venv.html>`_
for python 3.3, or `here <https://docs.python.org/3.4/library/venv.html>`_
for python 3.4.

Just make sure of have it created and activated while following the IEPY installation instructions.
Some small notes before leading you to the good documentation:

 - If you are working with python3.3, be warn that you will need to install *pip* by hand, as explained `here <http://pip.readthedocs.org/en/latest/installing.html#install-pip>`_
