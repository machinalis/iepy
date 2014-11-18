==================
Troubleshooting
==================


32 bit architecture issues
--------------------------

We've experience some memory issues when using a computer with 32 bit architecture. This is because by default we use the
Stanford CoreNLP (java based), which has some special needs about the memory. Read about them more in detail `here <http://nlp.stanford.edu/software/tagger.shtml>`__

We quote:

    The system requires Java 1.8+ to be installed. Depending on whether you're running 32 or 64 bit Java and the complexity of the tagger model, you'll need somewhere between 60 and 200 MB of memory to run a trained tagger (i.e., you may need to give java an option like java -mx200m)

What have worked for us is adding the following environment variable before running iepy:

.. code-block:: bash

    export _JAVA_OPTIONS='-Xms1024M -Xmx1024m'

You can modify those numbers to your convenience.


Preprocess not running under MacOS
----------------------------------

    Problems with the preprocess under MacOS? Apparently a change in the CoreNLP script is needed to
    be run. You need to change the file ``corenlp.sh`` that is located on
    ``/Users/<your user>/Library/Application Support/iepy/stanford-corenlp-full-2014-08-27/``
    and change ``scriptdir=`dirname $0``` for ``scriptdir=`dirname "$0"``` (ie, add double quotes around ``$0``)
