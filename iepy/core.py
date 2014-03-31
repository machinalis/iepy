# -*- coding: utf-8 -*-
from collections import defaultdict, namedtuple
import itertools

Fact = namedtuple("Fact", "e1 relation e2")
# An Evidence is a pair of a Fact and a TextSegment
Evidence = namedtuple("Evidence", "fact segment")


def certainty(p):
    return 0.5 + abs(p - 0.5)


class Knowledge(dict):
    """Maps evidence to a score in [0...1]

    None is also a valid score for cases when no score information is available
    """
    __slots__ = ()

    def by_certainty(self):
        """
        Returns an iterable over the evidence, with the most certain evidence
        at the front and the least certain evidence at the back. "Certain"
        means a score close to 0 or 1, and "uncertain" a score closer to 0.5.
        Note that a score of 'None' is considered as 0.5 here
        """
        return sorted(self.items(), key=lambda e, s: certainty(self[e]) if self[e] is not None else 0, reverse=True)

    def per_relation(self):
        """
        Returns a dictionary: relation -> Knowledge, where each value is only
        the knowledge for that specific relation
        """
        result = defaultdict(Knowledge)
        for e, s in self.items():
            result[e.fact.relation][e] = s
        return result


class BoostrappedIEPipeline(object):
    """
    From the user's point of view this class is meant to be used like this:
        p = BoostrappedIEPipeline(db_connector, seed_facts)
        p.start()  # blocking
        while UserIsNotTired:
            for question in p.questions_available():
                # Ask user
                # ...
                p.add_answer(question, answer)
            p.force_process()
        facts = p.get_facts()  # profit
    """

    def __init__(self, db_connector, seed_facts):
        """
        Not blocking.
        """
        self.db_con = db_connector
        self.seed_facts = Knowledge({Evidence(f, None): 1 for f in seed_facts})
        self.evidence_threshold = 0.99
        self.fact_threshold = 0.99
        self.knowledge = Knowledge()
        self.questions = Knowledge()
        self.answers = {}

        self.steps = [
                self.generalize_evidence,    # Step 1
                self.generate_questions,     # Step 2, first half
                None,                        # Pause to wait question answers
                self.filter_evidence,        # Step 2, second half
                self.learn_fact_extractors,  # Step 3
                self.extract_facts,          # Step 5
                self.filter_facts            # Step 6
            ]
        self.step_iterator = itertools.cycle(self.steps)

        # Build relation description: a map from relation labels to pairs of entity kinds
        self.relations = {}
        for e1, rel, e2 in seed_facts:
            t1 = e1.kind
            t2 = e1.kind
            if rel in self.relations and (t1, t2) != self.relations[rel]:
                raise ValueError("Ambiguous kinds for relation %r" % rel)
            self.relations[rel] = (t1, t2)

    def do_iteration(self, data):
        for step in self.step_iterator:
            if step is None:
                return
            data = step(data)

    ###
    ### IEPY User API
    ###

    def start(self):
        """
        Blocking.
        """
        self.do_iteration(self.seed_facts)

    def questions_available(self):
        """
        Not blocking.
        Returned value won't change until a call to `add_answer` or
        `force_process`.
        If `id` of the returned value hasn't changed the returned value is the
        same.
        The questions avaiable are a list of evidence.
        """
        return self.questions.by_certainty()

    def add_answer(self, evidence, answer):
        """
        Blocking (potentially).
        After calling this method the values returned by `questions_available`
        and `known_facts` might change.
        """
        self.answers[evidence] = int(answer)

    def force_process(self):
        """
        Blocking.
        After calling this method the values returned by `questions_available`
        and `known_facts` might change.
        """
        self.do_iteration(tuple())

    def known_facts(self):
        """
        Not blocking.
        Returned value won't change until a call to `add_answer` or
        `force_process`.
        If `len` of the returned value hasn't changed the returned value is the
        same.
        """
        return self.knowledge

    ###
    ### Pipeline steps
    ###

    def generalize_evidence(self, evidence):
        """
        Pseudocode. Stage 1 of pipeline.
        """
        self.knowledge.update(evidence)
        return Knowledge(
            (Evidence(fact, segment), None)
            for fact, _ in self.knowledge
            for segment in self.db_con.segments.get_segments_with_entities(fact.e1, fact.e2)
        )

    def generate_questions(self, evidence):
        """
        Pseudocode. Stage 2.1 of pipeline.
        confidence can implemented using the output from step 5 or accessing
        the classifier in step 3.

        Stores questions in self.questions and stops
        """
        self.questions = Knowledge((e, self._confidence(e)) for e in evidence if e not in self.answers)

    def filter_evidence(self):
        """
        Pseudocode. Stage 2.2 of pipeline.
        sorted_evidence is [(score, segment, (a, b, relation)), ...]
        answers is {(segment, (a, b, relation)): is_evidence, ...}
        """
        evidence = Knowledge(self.answers)
        evidence.update(
            (e, score < 0.5)
            for e, score in self.questions.items()
            if certainty(score) > self.evidence_threshold and e not in self.answers
        )
        return evidence

    def learn_fact_extractors(self, evidence):
        """
        Pseudocode. Stage 3 of pipeline.
        evidence is [(segment, (a, b, relation), is_evidence), ...]
        """
        classifiers = {}
        for rel, k in evidence.per_relation.iteritems():
            classifiers[rel] = object()  # TODO: instance classifier
            classifiers[rel].fit(k)
        return classifiers

    def extract_facts(self, extractors):
        """
        Pseudocode. Stage 5 of pipeline.
        extractors is a dict {relation: classifier, ...}
        """
        # TODO: this probably is smarter as an outer iteration through segments
        # and then an inner iteration over relations

        result = Knowledge()

        for r in extractors:
            lkind, rkind = self.relations[r]
            for segment in self.db_con.segments.segments_with_both_kinds(lkind, rkind):
                for e1, e2 in segment.entity_pairs(lkind, rkind):
                    f = Fact(e1, r, e2)
                    e = Evidence(f, segment)
                    result[e] = extractors[r].predict(e)
        return result

    def filter_facts(self, facts):
        """
        Pseudocode. Stage 6 of pipeline.
        facts is [((a, b, relation), confidence), ...]
        """
        return Knowledge((e, s) for e, s in facts.items() if s > self.fact_threshold)

    ###
    ### Aux methods
    ###
    def _confidence(self, segment, fact):
        """
        Returns a probability estimation of segment being an manifestation of
        fact.
        fact is (a, b, relation).
        """
        # FIXME: to be implemented on ticket IEPY-47
        return 0.5


def _all_entity_pairs(segment):
    """
    Aux method, returns all entity pairs in a segment.
    Order is important, so expect (a, b) and (b, a) in the answer.
    """
    raise NotImplementedError


def _relation_is_compatible(a, b, relation):
    """
    Aux method, returns True if a and b have types compatible with
    relation.
    """
    raise NotImplementedError
