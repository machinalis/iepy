"""
IEPY's reference corpus generation utility.

Usage:
    generate_reference_corpus.py <dbname> <relation_name> <kind_a> <kind_b> <output_filename> [options]
    generate_reference_corpus.py -h | --help | --version

Options:
  -h --help             Show this screen
  --version             Version number
  -c --continue         Load output filename and reuse the answers.
"""
from docopt import docopt

from iepy.db import connect, get_entity
from scripts.generate_seeds import label_evidence_from_oracle, human_oracle
from scripts.cross_validate import load_evidence_from_csv
from iepy.utils import save_labeled_evidence_to_csv
from iepy.models import Entity
from iepy.core import Evidence, Fact


class CombinedOracle(object):

    def __init__(self, knowledge, relation):
        self.knowledge = knowledge
        self.relation = relation

    def __call__(self, s, e1, e2):
        # bulid evidence:
        entity1 = get_entity(e1.kind, e1.key)
        entity2 = get_entity(e2.kind, e2.key)
        fact = Fact(e1=entity1, relation=self.relation, e2=entity2)
        o1 = s.entities.index(e1)
        o2 = s.entities.index(e2)
        evidence = Evidence(fact, s, o1, o2)
        if evidence in self.knowledge:
            answer = self.knowledge[evidence]
            assert answer in [0, 1]
            if answer == 0:
                return 'n'
            else:
                return 'y'
        else:
            return human_oracle(s, e1, e2)


if __name__ == '__main__':
    opts = docopt(__doc__, version=0.1)
    connector = connect(opts['<dbname>'])

    relation_name = opts['<relation_name>']
    kind_a = opts['<kind_a>']
    kind_b = opts['<kind_b>']
    output_filename= opts['<output_filename>']
    cont = opts['--continue']

    if cont:
        knowledge = load_evidence_from_csv(output_filename, connector)
        oracle = CombinedOracle(knowledge, relation_name)
    else:
        oracle = human_oracle

    r = label_evidence_from_oracle(kind_a, kind_b, oracle)
    # insert relation name:
    r2 = [(s, e1, e2, relation_name, label) for (s, e1, e2, label) in r]
    save_labeled_evidence_to_csv(r2, output_filename)

