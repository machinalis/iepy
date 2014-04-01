"""
Run IEPY core loop

Usage:
    iepy_runner.py <dbname> <seeds_file>
    iepy_runner.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
import codecs
from csv import reader
import pprint

from docopt import docopt

from iepy.core import BoostrappedIEPipeline, Fact
from iepy import db
from iepy.human_validation import TerminalInterviewer


def load_facts_from_csv(filepath):
    """Returns an iterable of facts from a CSV file encoded in UTF-8.
    It's assumend that first 4 columns are
        entity a kind, entity a key, entity b kind, entity b key
    and that the 5th column is the relation name.
    Everything else in the file will be ignored.
    Row with less column than stated, will be ignored.
    """
    with codecs.open(filepath, mode='r', encoding='utf-8') as csvfile:
        factsreader = reader(csvfile, delimiter=',')
        for row in factsreader:
            if len(row) < 5:
                continue
            entity_a = db.get_entity(row[0], row[1])
            entity_b = db.get_entity(row[2], row[3])
            yield Fact(entity_a, row[4], entity_b)


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connection = db.connect(opts['<dbname>'])
    seed_facts = load_facts_from_csv(opts['<seeds_file>'])
    p = BoostrappedIEPipeline(connection, seed_facts)

    STOP = 'STOP'

    p.start()  # blocking
    keep_looping = True
    while keep_looping:
        qs = list(p.questions_available())
        if not qs:
            keep_looping = False
        term = TerminalInterviewer(qs, p.add_answer, [(STOP, 'Stop execution asap')])
        result = term()
        if result == STOP:
            keep_looping = False
        p.force_process()
    facts = p.known_facts()  # profit
    pprint.pprint(facts)
