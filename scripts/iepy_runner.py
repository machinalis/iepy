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
from iepy.data.models import Relation, SegmentToTag, TextSegment
from iepy.extraction.terminal import TerminalInterviewer


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

    # Load evidences
    CEM = CandidateEvidenceManager  # shorcut
    labeled_evidences = CEM.labeled_candidates_for_relation(
        relation, CEM.conflict_resolution_newest_wins)

    iextractor = ActiveLearningCore(relation, labeled_evidences)
    iextractor.start()

    STOP = u'STOP'
    term = TerminalAdministration((STOP, u'Stop execution ASAP'))

    run_number = 0
    while iextractor.questions:
        segment_ids_to_add = []
        for evidence_candidate in iextractor.questions:
            segment = evidence_candidate.segment
            if segment.id not in segment_ids_to_add:
                segment_ids_to_add.append(evidence_candidate.segment.id)

        for segment_id in segment_ids_to_add:
            segment_to_tag = SegmentToTag(
                segment=TextSegment.object.get(id=segment_id),
                run_number=run_number,
            )
            segment_to_tag.save()

        result = term()
        if result == STOP:
            break

        # iextractor.add_answers(new_answers)
        iextractor.process()
        run_number += 1

    predictions = iextractor.predict()
    print("Predictions:")
    for prediction, value in predictions.items():
        print("({} -- {})".format(prediction, value))
