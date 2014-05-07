import codecs
from collections import defaultdict, namedtuple
from csv import DictReader, writer

from colorama import Fore, Style


def certainty(p):
    return 0.5 + abs(p - 0.5) if p is not None else 0.5


class Knowledge(dict):
    """Maps evidence to a score in [0...1]

    None is also a valid score for cases when no score information is available
    """
    CSV_COLUMNS = [
        u'entity a kind', u'entity a key', u'entity b kind', u'entity b key',
        u'relation name', u'document name', u'segment offset',
        u'entity a index', u'entity b index', u'label']
    __slots__ = ()

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

    def per_relation(self):
        """
        Returns a dictionary: relation -> Knowledge, where each value is only
        the knowledge for that specific relation
        """
        result = defaultdict(Knowledge)
        for e, s in self.items():
            result[e.fact.relation][e] = s
        return result

    def save_to_csv(self, filepath):
        """Writes labeled evidence to a CSV file encoded in UTF-8.

        The output CSV format can be see on CSV_COLUMNS.
        """
        with codecs.open(filepath, mode='w', encoding='utf-8') as csvfile:
            evidence_writer = writer(csvfile, delimiter=',')
            for (evidence, label) in self.items():
                entity_a = evidence.fact.e1
                entity_b = evidence.fact.e2
                evidence_writer.writerow([
                    entity_a.kind, entity_a.key,
                    entity_b.kind, entity_b.key,
                    evidence.fact.relation,
                    evidence.segment.document.human_identifier if evidence.segment else "",
                    evidence.segment.offset if evidence.segment else "",
                    evidence.o1, evidence.o2,
                    label
                ])


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

    default_color_1 = Fore.RED
    default_color_2 = Fore.GREEN

    def colored_text(self, color_1=None, color_2=None):
        """Will return a naive formated text with entities remarked.
        Assumes that occurrences does not overlap.
        """
        color_1 = color_1 or self.default_color_1
        color_2 = color_2 or self.default_color_2

        occurr1 = self.segment.entities[self.o1]
        occurr2 = self.segment.entities[self.o2]
        tkns = self.segment.tokens[:]
        if self.o1 < self.o2:
            tkns.insert(occurr2.offset_end, Style.RESET_ALL)
            tkns.insert(occurr2.offset, color_2)
            tkns.insert(occurr1.offset_end, Style.RESET_ALL)
            tkns.insert(occurr1.offset, color_1)
        else:  # must be solved in the reverse order
            tkns.insert(occurr1.offset_end, Style.RESET_ALL)
            tkns.insert(occurr1.offset, color_1)
            tkns.insert(occurr2.offset_end, Style.RESET_ALL)
            tkns.insert(occurr2.offset, color_2)
        return u' '.join(tkns)

    def colored_fact(self, color_1=None, color_2=None):
        color_1 = color_1 or self.default_color_1
        color_2 = color_2 or self.default_color_2

        return u'(%s <%s>, %s, %s <%s>)' % (
            color_1 + self.fact.e1.key + Style.RESET_ALL,
            self.fact.e1.kind,
            self.fact.relation,
            color_2 + self.fact.e2.key + Style.RESET_ALL,
            self.fact.e2.kind,
        )

    def colored_fact_and_text(self, color_1=None, color_2=None):
        color_1 = color_1 or self.default_color_1
        color_2 = color_2 or self.default_color_2

        return (
            self.colored_fact(color_1, color_2),
            self.colored_text(color_1, color_2)
        )
