.. IEPY documentation master file, created by
   sphinx-quickstart on Wed Apr 23 20:02:15 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to IEPY's documentation!
================================

IEPY is a framework for doing information extraction on unstructured
documents. It uses partially supervised machine learning techniques (i.e.,
there's a human helping the application, but the application generalizes what
the human does and learns).

Typical applications have a set of text documents as input (for example a
Wiki, or a database of patent applications). Those documents refer to some
*entities* of different *kinds* (for example “Albert Einstein” may be an
entity of kind “person” and “physicist” is an entity of kind “profession”).
The application defines the relevant kinds and the relations between those
kinds to extract (for example “*person* HAD-PROFESSION *profession*”). The
other input required is a set of *seed facts*, which are facts known to be
true, for example “Albert Einstein HAD-PROFESSION physicist”.

From that information, a IEPY application is able to find other examples of the
relation in the input documents, between the entities provided (example:
“Albert Einstein HAD-PROFESSION patent clerk”) or even between other
unrelated entities (example: “Ernest Hemingway HAD-PROFESSION writer”). These
extracted facts are also tagged with fragments of the original documents
that are evidence of the fact (example: “In late 1919 Ernest Hemingway began
as a freelancer, staff writer, and foreign correspondent for the Toronto Star
Weekly.”). During the extraction process, a person helps the system by replying
yes/no to questions of the form “Does this text fragment reflect this other
fact?”


Contents:

.. toctree::
   :maxdepth: 2

   installation
   tutorial
   instantiation
   active_learning_tutorial
   rules_tutorial
   corpus_labeling
   reference


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

