Running the rule based core
===========================

Here we will guide you through the steps to use the rule based system
to detect relations on the documents.


How they work
-------------

In the rule based system, you have to define a set of "regular expression like" rules
that will be tested against the segments of the documents. Roughly speaking,
if a rule matches it means that the relation is present.

This is used to acquire high precision because you control exactly what is matched.


Anatomy of a rule
-----------------

.. note::
    If you don't know how to define a python function,
    `check this out <https://docs.python.org/3/tutorial/controlflow.html#defining-functions>`_


A rule is basically a *decorated python function*.
We will see where this needs to be added later, for now lets concentrate on how it is written.

.. code-block:: python

    @rule(True)
    def born_date_and_death_in_parenthesis(Subject, Object):
        """ Example: Carl Bridgewater (January 2, 1965 - September 19, 1978) was shot dead """
        anything = Star(Any())
        return Subject + Pos("-LRB-") + Object + Token("-") + anything + Pos("-RRB-") + anything

First you have to specify that your function is in fact a rule by using the **decorator @rule**.

As you can see in the first line, this is added on top of the function.
In this decorator you have to define if the rule is going to be *positive* or *negative*. A positive
function that matches will label the relations as present and a negative one will label it as not present.
You can define this by passing the True or False parameter to the rule decorator.

Then it comes the definition of the function. This functions takes two parameters: the **Subject** and the **Object**.
This are patterns that will be part of the regex that the function
has to return.

After that it comes the body of the function. Here it is constructed a regular expression. That needs to be
returned by the function.  This is not an ordinary regular expression, it
uses `ReFO <https://github.com/machinalis/refo>`_.
In ReFO you have to operate with objects that does some kind of check to the text segment.

For our example, we've chosen to look for the *Was Born* relation. Particularly we look for the date of birth of a
person when it is written like this:

::

    Carl Bridgewater (January 2, 1965 - September 19, 1978)

To match this kind of cases, we have to specify the regex as a sum of predicates. This will check if every
part matches.

Lets break the regular expression of the example into smaller parts:

    * **Subject**: matches if it is an entity of the kind of the relation's subject.
    * **Object**: matches if it is an entity of the kind of the relation's object.
    * **Pos**: matches the *part of speech* of the token examined.
    * **Token**: matches if the token literally the one specified.
    * **Any**: matches any token.


Setting priority
----------------

Using the **rule decorator**, you can set that a rule is more important than another, and because of that it should
try to match before.

IEPY will run the rules ordered decreasingly by its priority number, and the default priority is 0.

For example, to set a priority of 1 you do:

.. code-block:: python

    @rule(True, priority=1)
    def rule_name(Subject, Object):
        ...


Negative rules
--------------

If you spot that your rules are matching things erroneously, you can write a rule
that catches that before it is taken by a positive rule.

You do this by setting the rule as a *negative rule* using the decorator. Also is
recommended to set higher priority so it is checked before the other ones.

Example:


.. code-block:: python

    @rule(False, priority=1)
    def incorrect_labeling_of_place_as_person(Subject, Object):
        """
        Ex:  Sophie Christiane of Wolfstein (24 October 24, 1667 - 23 August 1737)

        Wolfstein is a *place*, not a *person*
        """
        anything = Star(Any())
        person = Plus(Pos("NNP") + Question(Token(",")))
        return anything + person + Token("of") + Subject + anything


Note that the parameters of the rule decorator are **False** and **priority=1**

Where do I place the rules
--------------------------

On your project's instance folder, there should be a *rules.py* file. All rules should be place
there along with a  **RELATION** variable that sets which relation is going to be used.

This is the file that will be loaded when you run the *iepy_rules_runner*.


Example
-------

This is a portion of the example provided with IEPY, you can view the `complete
file here <https://github.com/machinalis/iepy/blob/develop/examples/birthdate/was_born_rules_sample.py>`__.

.. code-block:: python

    from refo import Question, Star, Any, Plus
    from iepy.extraction.rules_core import rule, Token, Pos

    RELATION = "was born"

    @rule(True)
    def was_born_explicit_mention(Subject, Object):
        """
        Ex: Shamsher M. Chowdhury was born in 1950.
        """
        anything = Star(Any())
        return anything + Subject + Token("was born") + Pos("IN") + Object + anything


    @rule(True)
    def is_born_in(Subject, Object):
        """
        Ex: Xu is born in 1902 or 1903 in a family of farmers in Hubei ..
        """
        anything = Star(Any())
        return Subject + Token("is born in") + Object + anything


    @rule(True)
    def just_born(Subject, Object):
        """
        Ex: Lyle Eugene Hollister, born 6 July 1923 in Sioux Falls, South Dakota, enlisted in the Navy....
        """
        anything = Star(Any())
        return Subject + Token(", born") + Object + anything


Testing your rules
------------------

During the construction of your rules, you might want to check wether if the rules are matching or if they
aren't. Even more, if you have tagged data in your corpus, you can know how good is the performance.

The rules tester is located on your isntance under the ``bin`` directory, it's called ``rules_tester.py``

You can run the tester with every rule or with a single rule, on all of the segments or in a sample of those.
Take a look at the parameters on the rules tester to find out how to use them by running:

.. code-block:: bash

    $ python bin/rules_tester.py --help
