# -*- coding: utf-8 -*-
import itertools


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
        self.seed_facts = seed_facts
        self.evidence_threshold = 0.99
        self.fact_threshold = 0.99
        self.facts = set()
        self.questions = []
        self.answers = {}

        self.steps = [
                self.generate_evidence,      # Step 1
                self.generate_questions,     # Step 2, first half
                None,                        # Pause to wait question answers
                self.filter_evidence,        # Step 2, second half
                self.learn_fact_extractors,  # Step 3
                self.extract_facts,          # Step 5
                self.filter_facts            # Step 6
            ]
        self.step_iterator = itertools.cycle(self.steps)

    def do_iteration(self, data):
        for step in self.step_iterator:
            if step is None:
                return
            if isinstance(data, tuple):
                data = step(*data)
            else:
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
        The questions avaiable are a list of (segment, (a, b, relation)).
        """
        return self.questions

    def add_answer(self, question, answer):
        """
        Blocking (potentially).
        After calling this method the values returned by `questions_available`
        and `known_facts` might change.
        question is (segment, (a, b, relation)).
        """
        self.answers[question] = answer

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
        return self.facts

    ###
    ### Pipeline steps
    ###

    def generate_evidence(self, facts):
        """
        Stage 1 of pipeline.
         - facts are [(a, b, relation), ...]
        """
        self.facts.update(facts)
        for fact in self.facts:
            a, b, _ = fact
            # FIXME when architecture is done, decide:
            #  - what to do with database object? Is needed? Is the connection?
            #  - invoking segments_with_both_entities with that path is OUCH
            for segment in self.db_con.segments.segments_with_both_entities(a, b):
                yield segment, fact

    def generate_questions(self, evidence):
        """
        Pseudocode. Stage 2.1 of pipeline.
        evidence is [(segment, (a, b, relation)), ...]
        confidence can implemented using the output from step 5 or accessing
        the classifier in step 3.
        """
        xs = []
        for segment, fact in evidence:
            score = self._confidence(segment, fact)
            xs.append((score, segment, fact))
        xs.sort(key=lambda x: abs(x[0] - 0.5), reverse=True)
        self.questions = xs

    def filter_evidence(self):
        """
        Pseudocode. Stage 2.2 of pipeline.
        sorted_evidence is [(score, segment, (a, b, relation)), ...]
        answers is {(segment, (a, b, relation)): is_evidence, ...}
        """
        xs = list(self.questions)
        evidence = []
        while xs and xs[-1][0] > self.evidence_threshold:
            score, segment, fact = xs.pop()
            is_evidence = self.answers.get((segment, fact), score < 0.5)
            evidence.append((segment, fact, is_evidence))
        return evidence

    def learn_fact_extractors(self, evidence):
        """
        Pseudocode. Stage 3 of pipeline.
        evidence is [(segment, (a, b, relation), is_evidence), ...]
        """
        classifiers = {}
        # TODO: Split evidence into the different relations (below)
        evidence_per_relation = evidence
        for relation, evidence in evidence_per_relation.iteritems():
            classifier = object()  # TODO: instance classifier
            classifier.fit(evidence)
            classifiers[relation] = classifier
        return classifiers

    def extract_facts(self, extractors):
        """
        Pseudocode. Stage 5 of pipeline.
        extractors is a dict {relation: classifier, ...}
        """
        # FIXME: This is designed here differently than what was designed on
        # iepy.db.TextSegmentManager, making non-usable the method segments_with_both_kinds?
        for segment in self.database.segments.get_segments():
            for a, b in _all_entity_pairs(segment):
                for relation, extractor in extractors.iteritems():
                    if _relation_is_compatible(a, b, relation):
                        yield (a, b, relation), extractor.predict(a, b)

    def filter_facts(self, facts):
        """
        Pseudocode. Stage 6 of pipeline.
        facts is [((a, b, relation), confidence), ...]
        """
        for fact, confidence in facts:
            if confidence > self.fact_threshold:
                yield fact

    ###
    ### Aux methods
    ###
    def _confidence(self, segment, fact):
        """
        Returns a proability estimation of segment being an manifestation of
        fact.
        fact is (a, b, relation).
        """
        raise NotImplementedError


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
