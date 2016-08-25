IEPY
====

IEPY is an open source tool for
`Information Extraction <http://en.wikipedia.org/wiki/Information_extraction>`_
focused on Relation Extraction.

To give an example of Relation Extraction, if we are trying to find a
birth date in:

    `"John von Neumann (December 28, 1903 – February 8, 1957) was a Hungarian and
    American pure and applied mathematician, physicist, inventor and polymath."`

then IEPY's task is to identify "``John von Neumann``" and
"``December 28, 1903``" as the subject and object entities of the "``was born in``"
relation.

It's aimed at:
    - `users <http://iepy.readthedocs.org/en/latest/active_learning_tutorial.html>`_
      needing to perform Information Extraction on a large dataset.
    - `scientists <http://iepy.readthedocs.org/en/latest/how_to_hack.html>`_
      wanting to experiment with new IE algorithms.

Features
--------

    - `A corpus annotation tool <http://iepy.readthedocs.org/en/latest/corpus_labeling.html>`_
      with a `web-based UI <http://iepy.readthedocs.org/en/latest/corpus_labeling.html#document-based-labeling>`_
    - `An active learning relation extraction tool <http://iepy.readthedocs.org/en/latest/active_learning_tutorial.html>`_
      pre-configured with convenient defaults.
    - `A rule based relation extraction tool <http://iepy.readthedocs.org/en/latest/rules_tutorial.html>`_
      for cases where the documents are semi-structured or high precision is required.
    - A web-based user interface that:
        - Allows layman users to control some aspects of IEPY.
        - Allows decentralization of human input.
    - A shallow entity ontology with coreference resolution via `Stanford CoreNLP <http://nlp.stanford.edu/software/corenlp.shtml>`_
    - `An easily hack-able active learning core <http://iepy.readthedocs.org/en/latest/how_to_hack.html>`_,
      ideal for scientist wanting to experiment with new algorithms.

Installation
------------

Install the required packages:

.. code-block:: bash

    sudo apt-get install build-essential python3-dev liblapack-dev libatlas-dev gfortran openjdk-7-jre

Then simply install with **pip**:

.. code-block:: bash

    pip install iepy

Full details about the installation is available on the
`Read the Docs <http://iepy.readthedocs.org/en/latest/installation.html>`__ page.

Running the tests
-----------------

If you are contributing to the project and want to run the tests, all you have to do is:

    - Make sure your JAVAHOME is correctly set. `Read more about it here <http://iepy.readthedocs.io/en/latest/installation.html#install-iepy-package>`_
    - In the root of the project run `nosetests`

Learn more
----------

The full documentation is available on `Read the Docs <http://iepy.readthedocs.org/en/latest/>`__.


Authors
-------

IEPY is © 2014 `Machinalis <http://www.machinalis.com/>`_ in collaboration
with the `NLP Group at UNC-FaMAF <http://pln.famaf.unc.edu.ar/>`_. Its primary
authors are:

 * Rafael Carrascosa <rcarrascosa@machinalis.com> (rafacarrascosa at github)
 * Javier Mansilla <jmansilla@machinalis.com> (jmansilla at github)
 * Gonzalo García Berrotarán <ggarcia@machinalis.com> (j0hn at github)
 * Franco M. Luque <francolq@famaf.unc.edu.ar> (francolq at github)
 * Daniel Moisset <dmoisset@machinalis.com> (dmoisset at github)

You can follow the development of this project and report issues at
http://github.com/machinalis/iepy

You can join the mailing list `here <https://groups.google.com/forum/?hl=es-419#%21forum/iepy>`__
