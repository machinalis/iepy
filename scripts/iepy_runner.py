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
from iepy.data.db import CandidateEvidenceManager
from iepy.data.models import Relation
from iepy.extraction.terminal import TerminalAdministration


def print_all_relations():
    print("All available relations:")
    for relation in Relation.objects.all():
        print("  {}".format(relation))


def load_labeled_evidences(relation, evidences):
    CEM = CandidateEvidenceManager  # shorcut
    return CEM.labels_for(relation, evidences, CEM.conflict_resolution_newest_wins)

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

    candidates = CandidateEvidenceManager.candidates_for_relation(relation)
    labeled_evidences = load_labeled_evidences(relation, candidates)
    iextractor = ActiveLearningCore(relation, labeled_evidences)
    iextractor.start()

    STOP = u'STOP'
    term = TerminalAdministration(relation,
                                  extra_options=[(STOP, u'Stop execution ASAP')])

    while iextractor.questions:
        questions = list(iextractor.questions)  # copying the list
        term.update_candidate_evidences_to_label(questions)
        result = term()
        if result == STOP:
            break

        i = 0
        for c, label_value in load_labeled_evidences(relation, questions).items():
            if label_value is not None:
                iextractor.add_answer(c, label_value)
                i += 1
        print ('Added %s new human labels to the extractor core' % i)
        iextractor.process()

    predictions = iextractor.predict()
    print("Predictions:")
    for prediction, value in predictions.items():
        print("({} -- {})".format(prediction, value))
