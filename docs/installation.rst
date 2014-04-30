==================
IEPY installation
==================


This installation notes assume that you have a just installed *ubuntu 13.10
server*. If instead of that you have a *desktop* installation, or another
version, some details or software versions may be slightly different.
Given that IEPY can be installed both in python2.7 and python3.3 [1]_ or higher,
pay attention to the warning notes here and there explaining the small
differences.

.. [1] For python 3 IEPY is using an alpha release of NLTK.

Because of it's dependencies, installation it's not a single pip install, and requires a bit of extra work, but it's actually not that hard.

Outline:
    - install some system packages
    - install python libraries
    - (optional) install development tools
    - (optional) install example application


System software needed
======================

You need to install the following packages:

 - git (for getting the code from github)

Because of the need of aggregation, mongodb 2.2 or higher is required

 - mongodb-server
 - mongodb-clients

For scipy & numpy installation, you will also need:

 - liblapack-dev
 - libatlas-dev
 - gfortran
 - openjdk-7-jre

If you plan to install IEPY for python 2, please also install

 - python-dev
 - python-virtualenv (for creating your virtualenv)

But for python 3, install:

 - python3-dev


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

**Warning**, if you are using pip 1.5 (will probably be the case on python3) you will have to use the extra argument *--process-dependecy-links* as shown below, otherwise some packages (like nltk for python3) wont be available

.. code-block:: bash

    cd <path-to-gitrepo>
    pip install . --process-dependecy-links


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
