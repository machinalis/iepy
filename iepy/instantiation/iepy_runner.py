"""
Run IEPY core loop

Usage:
    iepy_runner.py [options] <relation_name>
    iepy_runner.py -h | --help | --version

Options:
  -h --help                          Show this screen
  --tune-for=<tune-for>              Predictions tuning. Options are high-prec or high-recall [default: high-prec]
  --extractor-config=<config.json>   Sets the extractor config
  --version                          Version number
"""

import json
import logging
from docopt import docopt
from sys import exit

import iepy
iepy.setup(__file__)

from iepy.extraction.active_learning_core import ActiveLearningCore, HIPREC, HIREC
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

    if opts['--tune-for'] == 'high-prec':
        tuning_mode = HIPREC
    elif opts['--tune-for'] == 'high-recall':
        tuning_mode = HIREC
    else:
        print ('Invalid tuning mode')
        print (__doc__)
        exit(1)

    try:
        relation = Relation.objects.get(name=relation)
    except Relation.DoesNotExist:
        print("Relation {!r} non existent".format(relation))
        print_all_relations()
        exit(1)

    extractor_config = opts.get("--extractor-config")
    if extractor_config:
        with open(extractor_config) as filehandler:
            extractor_config = json.load(filehandler)

    candidates = CandidateEvidenceManager.candidates_for_relation(relation)
    labeled_evidences = load_labeled_evidences(relation, candidates)
    iextractor = ActiveLearningCore(relation, labeled_evidences, extractor_config,
                                    performance_tradeoff=tuning_mode)
    iextractor.start()

    STOP = u'STOP'
    term = TerminalAdministration(relation,
                                  extra_options=[(STOP, u'Stop execution')])
    was_ever_trained = False
    while iextractor.questions:
        questions = list(iextractor.questions)  # copying the list
        term.update_candidate_evidences_to_label(questions)
        result = term()
        i = 0
        for c, label_value in load_labeled_evidences(relation, questions).items():
            if label_value is not None:
                iextractor.add_answer(c, label_value)
                i += 1
        print ('Added %s new human labels to the extractor core' % i)
        iextractor.process()
        was_ever_trained = True
        if result == STOP:
            break

    if not was_ever_trained:
        # It's needed to run some process before asking for predictions
        iextractor.process()
    predictions = iextractor.predict()
    print("Predictions:")
    for prediction, value in predictions.items():
        print("({} -- {})".format(prediction, value))
