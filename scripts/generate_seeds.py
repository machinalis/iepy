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

from future.builtins import input

from iepy.db import connect, TextSegmentManager, get_entity
from iepy.utils import save_facts_to_csv
from iepy.core import Evidence, Fact


def label_evidence_from_oracle(kind_a, kind_b, relation, oracle):
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
                # bulid evidence:
                entity1 = get_entity(e1.kind, e1.key)
                entity2 = get_entity(e2.kind, e2.key)
                if entity1 == entity2:
                    # not tolerating reflectiveness for now
                    continue
                fact = Fact(e1=entity1, relation=relation, e2=entity2)
                o1 = s.entities.index(e1)
                o2 = s.entities.index(e2)
                evidence = Evidence(fact, s, o1, o2)

                # ask the oracle: are e1 and e2 related in s?
                answer = oracle(evidence)
                assert answer in ['y', 'n', 'stop']
                if answer == 'y':
                    result += [(evidence, True)]
                elif answer == 'n':
                    result += [(evidence, False)]
                elif answer == 'stop':
                    return result
    return result


def human_oracle(evidence):
    """Simple text interface to query a human for fact generation."""
    colored_fact, colored_segment = evidence.colored_fact_and_text()
    print('SEGMENT:', colored_segment)
    question = ' FACT: {0}? (y/n/stop) '.format(colored_fact)
    answer = input(question)
    while answer not in ['y', 'n', 'stop']:
        answer = input(question)
    return answer


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connect(opts['<dbname>'])

    relation_name = opts['<relation_name>']
    kind_a = opts['<kind_a>']
    kind_b = opts['<kind_b>']
    output_filename = opts['<output_filename>']

    r = label_evidence_from_oracle(kind_a, kind_b, relation_name, human_oracle)
    facts = [ev.fact for (ev, label) in r if label]
    save_facts_to_csv(facts, output_filename)
