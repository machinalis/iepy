Gazettes resolution
===================

We call a gazette a mapping between a list of tokens and an entity kind. If that list of tokens
matches exactly on your text, then that would be tagged as an entity. 

All the entities occurrences that where detected by a gazette and share the same set of tokens, will share the same entity.
This means that if you have a gazette that finds ``Dr. House`` and taggs it as a ``PERSON``, all the occurrences in the text
that matches those tokens, will belong to the same entity.

Basic usage: Loading from csv
-----------------------------

The basic usage would be including a set of gazettes before running the preprocess step. To include
the gazettes on your database, you can use the script ``gazettes_loader.py`` that comes included with
your instance. This will take a csv file with the following format:

::

    <literal>,<class>

Literal can be a single token or multiple tokens separated by space.
The only restriction is that every literal is unique.

For example, a gazettes csv file could be:

::

    literal,class
    Dr. House,PERSON
    Lupus,DISEASE
    Headache,SYMPTOMS


Loading from Freebase
---------------------

.. note::

    Freebase is a large collaborative knowledge base. Learn more about 
    it on `www.freebase.com <http://www.freebase.com/>`__

If you desire to generate a set of gazettes automatically using data from freebase, you can use the following option
of the gazettes loader:

::

    gazettes_loader.py --freebase_type=<freebase_type> <KIND>

This will query freebase and find instances of the type that you specified. Then it will create a gazette for each
of those instances, use the name and the kind that you gave.
Make sure that ``<freebase_type>`` it's a freebase path to a type.

Lets see an example, running:

::

   python bin/gazettes_loader.py --freebase_type=/location/country COUNTRY 

would generate a `list of countries <http://www.freebase.com/location/country?instances=>`__ and load your gazettes with them.

.. note::

    Freebase is in constant change so running this script in different moments may generate
    different output.


Removing elements
-----------------

When deleting an entity, all the occurrences are deleted with it along the gazette item that introduced them.
Same goes the other way, if you delete a gazette item, the entity, and therefore the occurrences, will be deleted as well.

To delete a gazette item, go to the database admin page and find the Gazette section. You'll be able to find the one that you want
to remove.

To remove an entity, find an occurrence by exploring a document on any of its views, and right click it. There you'll find a delete
link that enables you to remove the whole entity. Keep in mind that this action will delete the gazette item.
