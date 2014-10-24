Running the active learning core
================================

The active learning core can be run doing:

.. code-blocK:: bash

    python bin/iepy_runner.py <relation_name>

This will run until it needs you to label some of the evidences. At this point, what you
need to do is go to the web interface that you ran on the previous step, and there you
can label some evidences.

When you consider that is enough, go to the prompt that the iepy runner presented you,
and continue the execution by typing **run**.

That will cycle again and repeat the process.
