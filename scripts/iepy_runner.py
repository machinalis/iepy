"""
Run IEPY core loop

Usage:
    iepy_runner.py <dbname> <relation_ids> <output_file> [--gold=<gold_standard>]
    iepy_runner.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt
import logging
from sys import exit

from iepy.extraction.active_learning_core import BootstrappedIEPipeline
from iepy.data.db import RelationManager
from iepy.data.knowledge import Knowledge
from iepy.extraction.human_validation import TerminalInterviewer


def parse_relations(relation_ids_csv):
    result = []
    all_relations = RelationManager.dict_by_id()
    for r_id in relation_ids_csv.split(','):
        try:
            r_id = int(r_id)
        except:
            pass
        if r_id not in all_relations:
            logging.error(
                'All possible relations are: %s. "%s" is not a valid relation id' % (
                    ', '.join(['%s (%s)' % (k, v.name) for k, v in all_relations.items()]),
                    r_id
                )
            )
            exit(1)
        result.append(all_relations[r_id])
    return result

if __name__ == u'__main__':
    opts = docopt(__doc__, version=0.1)
    relations = parse_relations(opts['<relation_ids>'])
    output_file = opts[u'<output_file>']
    gold_standard_file = opts[u'--gold']
    if gold_standard_file:
        gold_standard = Knowledge.load_from_csv(gold_standard_file)
    else:
        gold_standard = None

    p = BootstrappedIEPipeline(relations, gold_standard)

    logging.basicConfig(level=logging.DEBUG,
                        format=u"%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    STOP = u'STOP'

    p.start()  # blocking
    keep_looping = True
    while keep_looping:
        qs = list(p.questions_available())
        if not qs:
            keep_looping = False
        term = TerminalInterviewer(qs, p.add_answer, [(STOP, u'Stop execution ASAP')])
        result = term()
        if result == STOP:
            keep_looping = False
        else:
            p.force_process()
    facts = p.known_facts()  # profit
    facts.save_to_csv(output_file)
