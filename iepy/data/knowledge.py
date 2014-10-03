from collections import defaultdict, namedtuple, OrderedDict

from colorama import Fore, Style

from iepy.data import db
from iepy.human_validation import Answers
from iepy.pycompatibility import py_compatible_csv


def certainty(p):
    return 0.5 + abs(p - 0.5) if p is not None else 0.5


class Knowledge(OrderedDict):
    """Maps evidence to a score in [0...1]

    None is also a valid score for cases when no score information is available
    """
    CSV_COLUMNS = [
        u'entity a kind', u'entity a key', u'entity b kind', u'entity b key',
        u'relation name', u'document name', u'segment offset',
        u'entity a tokens offset', u'entity b tokens offset', u'label']
    __slots__ = ()

    def __eq__(self, other):
        """Only comparing the mapping evidence -> score
        and just that, not the ordering, so...
        """
        return dict(self) == dict(other)

    def by_certainty(self):
        """
        Returns an iterable over the evidence, with the most certain evidence
        at the front and the least certain evidence at the back. "Certain"
        means a score close to 0 or 1, and "uncertain" a score closer to 0.5.
        Note that a score of 'None' is considered as 0.5 here
        """
        def key_funct(e_s):
            e = e_s[0]
            return (certainty(self[e]) if self[e] is not None else 0, e)
        return sorted(self.items(), key=key_funct, reverse=True)

    def by_score(self, reverse=False):
        """
        Returns an iterable over the evidence sorted by score, in increasing
        order if reverse=False (default), in decreasing order if reverse=True.
        """
        return sorted(self.items(), key=lambda x: x[1], reverse=reverse)

    def per_relation(self):
        """
        Returns a dictionary: relation -> Knowledge, where each value is only
        the knowledge for that specific relation
        """
        result = defaultdict(Knowledge)
        for e, s in self.items():
            result[e.relation][e] = s
        return result

    def save_to_csv(self, filepath):
        """Writes labeled evidence to a CSV file encoded in UTF-8.

        The output CSV format can be seen on CSV_COLUMNS.
        """
        def sort_funct(x):
            ev, score = x
            if not ev.segment:
                return (None, None, ev.fact)
            else:
                return (ev.segment.document, ev.segment, ev.fact)
        with py_compatible_csv.writer(filepath) as evidence_writer:
            for (evidence, label) in sorted(self.items(),
                                            key=sort_funct):
                fact = evidence.fact
                segm = evidence.segment
                entity_a = fact.e1
                entity_b = fact.e2
                row = [entity_a.kind, entity_a.key,
                       entity_b.kind, entity_b.key,
                       fact.relation]
                if segm:
                    row.extend(
                        [segm.document.human_identifier,
                         segm.offset,
                         segm.entities[evidence.o1].offset,
                         segm.entities[evidence.o2].offset,
                         label
                         ]
                    )
                else:
                    row.extend(
                        [u"",
                         u"",
                         None,
                         None,
                         label
                         ]
                    )
                evidence_writer.writerow(row)

    @classmethod
    def load_from_csv(cls, filename):
        """The CSV format can be seen on CSV_COLUMNS."""
        result = cls()
        with py_compatible_csv.DictReader(filename, fieldnames=cls.CSV_COLUMNS) as csv_reader:
            for row_idx, row in enumerate(csv_reader):
                entity_a = db.get_entity(row[u'entity a kind'],
                                         row[u'entity a key'])
                entity_b = db.get_entity(row[u'entity b kind'],
                                         row[u'entity b key'])
                f = Fact(entity_a, row[u'relation name'], entity_b)
                if row[u'document name']:
                    s = db.TextSegmentManager.get_segment(
                        row[u'document name'],
                        int(row[u'segment offset']))

                    occurrences_dict = dict(
                        ((e_o.offset, e_o.kind), idx)
                        for idx, e_o in enumerate(s.entities)
                    )
                    start_occur_a = int(row[u'entity a tokens offset'])
                    start_occur_b = int(row[u'entity b tokens offset'])
                    idx_a = occurrences_dict.get((start_occur_a, entity_a.kind), -1)
                    idx_b = occurrences_dict.get((start_occur_b, entity_b.kind), -1)
                    if -1 in [idx_a, idx_b]:
                        print(u"Row %i skipped because it's entity occurrences are wrong"
                              % row_idx)
                        continue

                    ev = Evidence(fact=f, segment=s, o1=idx_a, o2=idx_b)
                else:
                    # fact with no evidence.
                    ev = Evidence(fact=f, segment=None, o1=None, o2=None)
                raw_label = row[u'label']
                try:
                    label = float(raw_label)
                except (TypeError, ValueError):
                    if raw_label == "True":
                        label = Answers.values[Answers.YES]
                    elif raw_label == "False":
                        label = Answers.values[Answers.NO]
                    else:
                        label = None
                result[ev] = label
        return result

    def extend_from_oracle(self, kind_a, kind_b, relation, oracle):
        """Uses an oracle for extending the knowledge.

        The oracle is a function that takes three parameters: the text segment and
        the two entity occurrences (for an example, see human_oracle() below). It
        must return 'y', 'n', 'd' or 'stop', meaning respectively that the relation holds,
        that it doesn't, that you don't know, and that the oracle wants to stop answering.

        Will first check with the oracle all the unknown evidences already stored on the
        knowledge. After that, will explore the database for new evidences of the
        correspondent kinds and ask the oracle to label it.
        """
        # First, checking all the unknown existent ones
        dunno_value = Answers.values[Answers.DONT_KNOW]
        unknowns = [
            ev for ev, label in self.items()
            if label == dunno_value and ev.fact.relation == relation]
        if unknowns:
            print(u'Checking unknowns first (there are %s)' % len(unknowns))
            for evidence in unknowns:
                # ask again the oracle: are e1 and e2 related in s?
                answer = oracle(evidence, Answers.options)
                assert answer in Answers.options
                if answer == Answers.STOP:
                    return
                else:
                    self[evidence] = Answers.values[answer]

        # And now, explore other possibilities
        manager = db.TextSegmentManager()
        ss = manager.segments_with_both_kinds(kind_a, kind_b)
        for i, s in enumerate(ss):
            # cartesian product of all k1 and k2 combinations in the sentence:
            ka_entities = [e for e in s.entities if e.kind == kind_a]
            kb_entities = [e for e in s.entities if e.kind == kind_b]
            print(u'Considering segment %i of %i' % (i+1, len(ss)))
            for e1 in ka_entities:
                for e2 in kb_entities:
                    # build evidence:
                    if e1 == e2:
                        # not tolerating entityoccurrence reflectiveness for now
                        continue
                    entity1 = db.get_entity(e1.kind, e1.key)
                    entity2 = db.get_entity(e2.kind, e2.key)
                    fact = Fact(e1=entity1, relation=relation, e2=entity2)
                    o1 = s.entities.index(e1)
                    o2 = s.entities.index(e2)
                    evidence = Evidence(fact, s, o1, o2)
                    if evidence in self:
                        # we already have this answered
                        continue

                    # ask the oracle: are e1 and e2 related in s?
                    answer = oracle(evidence, Answers.options)
                    assert answer in Answers.options
                    if answer == Answers.STOP:
                        return
                    else:
                        self[evidence] = Answers.values[answer]
        return


# A fact is a triple with two Entity() instances and a relation label
Fact = namedtuple("Fact", "e1 relation e2")
BaseEvidence = namedtuple("Evidence", "fact segment o1 o2")


class Evidence(BaseEvidence):
    """
    An Evidence is a pair of a Fact and a TextSegment and occurrence indices.
    Evicence instances are tipically constructed whitin a
    BootstrappedIEPipeline and it attributes are meant to be used directly (no
    getters or setters) in a read-only fashion (it's an inmutable after all).

    Evidence instances are dense information and follow strict invariants so
    here is a small cheatsheet of its contents:

    * e                           -- Evidence instance
        * fact                    -- Fact instance
            * relation            -- A ``str`` naming the relation of the fact
            * e1                  -- Entity instance (an abstract entity, not an entity occurrence)
                * kind            -- A ``str`` naming the kind/type of entity
                * key             -- A ``str`` that uniquely identifies this entity
                * canonical_form  -- A ``str`` that's the human-friendly way to represent this entity
            * e2                  -- Entity instance (an abstract entity, not an entity occurrence)
                * kind            -- A ``str`` naming the kind/type of entity
                * key             -- A ``str`` that uniquely identifies this entity
                * canonical_form  -- A ``str`` that's the human-friendly way to represent this entity
        * segment                 -- A Segment instance
            * tokens              -- A list of ``str`` representing the tokens in the segment
            * text                -- The original text ``str`` of this document
            * sentences           -- A list of token indexes denoting the start of the syntactic sentences on the segment
            * postags             -- A list of ``str`` POS tags, in 1-on-1 relation with tokens
            * offset              -- An ``int``, the offset of the segment, in tokens, from the document start
            * entities            -- A list of entity occurrences
                * kind            -- A ``str`` naming the kind/type of entity
                * key             -- A ``str`` that uniquely identifies this entity
                * canonical_form  -- A ``str`` that's the human-friendly way to represent this entity
                * offset          -- An ``int``, the offset to the entity occurrence start, in tokens, from the segment start
                * offset_end      -- An ``int``, the offset to the entity occurrence end, in tokens, from the segment start
                * alias           -- A ``str``, the literal text manifestation of the entity occurrence
        * o1                      -- The index in segment.entities occurrence of the first entity
        * o2                      -- The index in segment.entities occurrence of the second entity


    And a commonly needed recipes:
        * ``e.segment.entities[e.o1]``: The occurrence of the first entity
        * ``e.segment.entities[e.o2]``: The occurrence of the second entity


    During initialization the segment+indices can be left out (as None).

    The following invariants apply:
     - ``e.segment == None`` iff ``e.o1 == None``
     - ``e.segment == None`` iff ``e.o2 == None``
     - ``e.o1 != None`` implies ``e.fact.e1.kind == e.segment.entities[e.o1].kind and e.fact.e1.key == e.segment.entities[e.o1].key``
     - ``e.o2 != None`` implies ``e.fact.e2.kind == e.segment.entities[e.o2].kind and e.fact.e2.key == e.segment.entities[e.o2].key``
    """
    __slots__ = []

