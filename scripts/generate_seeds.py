"""
IEPY's seed generation utility.

Usage:
    generate_seeds.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename>
    generate_seeds.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
"""
from docopt import docopt

from iepy.db import TextSegmentManager
from iepy.db import connect
from iepy.utils import save_facts_to_csv


def generate_facts_from_oracle(kind_a, kind_b, oracle):
    """The oracle is a function that takes three parameters: the text segment and
    the two entity occurrences (for an example, see human_oracle() below). It 
    must return 'y', 'n' or 'stop', meaning respectively that the relation holds,
    that it doesn't, and that the oracle wants to stop answering.
    """
    manager = TextSegmentManager()
    ss = manager.segments_with_both_kinds(kind_a, kind_b)
    result = []
    for s in ss:
        # cartesian product of all k1 and k2 combinations in the sentence:
        ka_entities = [e for e in s.entities if e.kind == kind_a]
        kb_entities = [e for e in s.entities if e.kind == kind_b]
        for e1 in ka_entities:
            for e2 in kb_entities:
                # ask the oracle: are e1 and e2 related in s?
                answer = oracle(s, e1, e2)
                if answer == 'y':
                    result += [(e1, e2, s)]
                elif answer == 'stop':
                    return result
    return result


def human_oracle(segment, entity_a, entity_b):
    """Simple text interface to query a human for fact generation."""
    print 'SEGMENT:', segment.text
    question = ' ENTITIES: {0}, {1}? (y/n/stop) '.format(entity_a, entity_b)
    answer = raw_input(question)
    while answer not in ['y','n', 'stop']:
        answer = raw_input(question)
    return answer


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])

    relation_name = opts['<relation_name>']
    kind_a = opts['<kind_a>']
    kind_b = opts['<kind_b>']
    output_filename= opts['<output_filename>']

    r = generate_facts_from_oracle(kind_a, kind_b, human_oracle)
    facts = [(e1, e2, relation_name) for (e1, e2, _) in r]
    save_facts_to_csv(facts, output_filename)

