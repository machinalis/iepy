"""
Run IEPY core loop

Usage:
    iepy_runner.py <relation_name>
    iepy_runner.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt
import logging
from sys import exit

from iepy.extraction.active_learning_core import ActiveLearningCore
from iepy.data.models import Relation
from iepy.extraction.human_validation import TerminalInterviewer


def print_all_relations():
    print("All available relations:")
    for relation in Relation.objects.all():
        print("  {}".format(relation))


if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    relation = opts['<relation_name>']

    logging.basicConfig(level=logging.DEBUG,
                        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    try:
        relation = Relation.objects.get(name=relation)
    except Relation.DoesNotExist:
        print("Relation {!r} non existent".format(relation))
        print_all_relations()
        exit(1)

    p = ActiveLearningCore(relation)

    STOP = u'STOP'

    p.start()
    while p.questions:
        term = TerminalInterviewer(p.questions, p.add_answer, [(STOP, u'Stop execution ASAP')])
        result = term()
        if result == STOP:
            break
        p.process()
    predictions = p.predict()
    print("Predictions:")
    for prediction, value in predictions.items():
        print("({} -- {})".format(prediction, value))
