.. IEPY documentation master file, created by
   sphinx-quickstart on Wed Apr 23 20:02:15 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IEPY's documentation!
================================

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
    - :doc:`users <active_learning_tutorial>`
      needing to perform Information Extraction on a large dataset.
    - :doc:`scientists <how_to_hack>`
      wanting to experiment with new IE algorithms.

Features
--------

    - :doc:`A corpus annotation tool <corpus_labeling>`
      with a `web-based UI <corpus_labeling.html#document-based-labeling>`_
    - :doc:`An active learning relation extraction tool <active_learning_tutorial>`
      pre-configured with convenient defaults.
    - :doc:`A rule based relation extraction tool <rules_tutorial>`
      for cases where the documents are semi-structured or high precision is required.
    - A web-based user interface that:
        - Allows layman users to control some aspects of IEPY.
        - Allows decentralization of human input.
    - A shallow entity ontology with coreference resolution via `Stanford CoreNLP <http://nlp.stanford.edu/software/corenlp.shtml>`_
    - :doc:`An easily hack-able active learning core <how_to_hack>`,
      ideal for scientist wanting to experiment with new algorithms.


Contents:
---------

.. toctree::
   :maxdepth: 2

   installation
   tutorial
   instantiation
   active_learning_tutorial
   rules_tutorial
   preprocess
   corpus_labeling
   how_to_hack


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


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

