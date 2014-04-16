IEPY
====

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

Installation
------------

Please check docs/install.rst

Documentation
-------------

Documentation will be available at http://iepy.readthedocs.org/en/latest/

Contact Information
-------------------

IEPY is © 2014 `Machinalis <http://www.machinalis.com/>`_ in collaboration
with the `NLP Group at UNC-FaMAF <http://pln.famaf.unc.edu.ar/>`_. Its primary
authors are:

 * Rafael Carrascosa <rcarrascosa@machinalis.com> (rafacarrascosa at github)
 * Franco M. Luque <francolq@famaf.unc.edu.ar> (francolq at github)
 * Javier Mansilla <jmansilla@machinalis.com> (jmansilla at github)
 * Daniel Moisset <dmoisset@machinalis.com> (dmoisset at github)

You can follow the development of this project and report issues at
http://github.com/machinalis/iepy

Licensing
---------

This project has a BSD license, as stated in the LICENSE file.

Changelog
---------

No stable releases yet. Coming soon.

The project is currently working, it has good testing coverage and a working
example. We're still missing some API cleanup, documentation, packaging and a
couple of large bugfixes.


