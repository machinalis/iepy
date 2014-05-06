from iepy.db import TextSegmentManager, get_entity
from iepy.core import Evidence, Fact

ANSWERS = [u'y', u'n', u'stop']


def label_evidence_from_oracle(kind_a, kind_b, relation, oracle):
    """The oracle is a function that takes three parameters: the text segment and
    the two entity occurrences (for an example, see human_oracle() below). It
    must return 'y', 'n' or 'stop', meaning respectively that the relation holds,
    that it doesn't, and that the oracle wants to stop answering.
    """
    manager = TextSegmentManager()
    ss = manager.segments_with_both_kinds(kind_a, kind_b)
    result = []
    for i, s in enumerate(ss):
        # cartesian product of all k1 and k2 combinations in the sentence:
        ka_entities = [e for e in s.entities if e.kind == kind_a]
        kb_entities = [e for e in s.entities if e.kind == kind_b]
        print(u'Considering segment %i of %i' % (i, len(ss)))
        for e1 in ka_entities:
            for e2 in kb_entities:
                # build evidence:
                if e1 == e2:
                    # not tolerating entittyoccurrence reflectiveness for now
                    continue
                entity1 = get_entity(e1.kind, e1.key)
                entity2 = get_entity(e2.kind, e2.key)
                fact = Fact(e1=entity1, relation=relation, e2=entity2)
                o1 = s.entities.index(e1)
                o2 = s.entities.index(e2)
                evidence = Evidence(fact, s, o1, o2)

                # ask the oracle: are e1 and e2 related in s?
                answer = oracle(evidence, ANSWERS)
                assert answer in ANSWERS
                if answer == u'y':
                    result += [(evidence, True)]
                elif answer == u'skip':
                    result += [(evidence, False)]
                elif answer == u'stop':
                    return result
    return result
