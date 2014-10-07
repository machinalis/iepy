from iepy import defaults
from iepy.data.models import LabeledRelationEvidence
from iepy.extraction.fact_extractor import FactExtractorFactory


class ActiveLearningCore:
    """
    Iepy's main class. Implements an active learning information extraction
    pipeline.

    From the user's point of view this class is meant to be used like this::

        p = BoostrappedIEPipeline(relation)
        p.start()  # blocking
        while UserIsNotTired and p.questions:
            question = p.questions[0]
            answer = ask_user(question)
            p.add_answer(question, answer)
            p.process()
        predictions = p.predict()  # profit
    """

    #
    # IEPY User API
    #

    def __init__(self, relation):
        self.relation = relation
        self.fact_extractor = None

    def start(self):
        """
        Blocking.
        """
        self.load_all_evidence_from_database()
        self.questions = self.candidate_evidence

    def add_answer(self, evidence, answer):
        """
        Not blocking.
        """
        assert answer in (True, False)
        self.labeled_evidence[evidence] = answer
        for list_ in (self.questions, self.candidate_evidence):  # TODO: Check performance. Should use set?
            try:
                list_.remove(evidence)
            except ValueError:
                pass  # Was not in list, no problem, right?
        # TODO: Save labeled evidence into database?

    def process(self):
        """
        Blocking.
        After calling this method the values returned by `questions_available`
        and `known_facts` will change.
        """
        yesno = set(self.labeled_evidence.values())
        assert len(yesno) <= 2, "Evidence is not binary!"
        if len(yesno) == 2:
            self.train_fact_extractor()
            self.rank_candidate_evidence()
            self.choose_questions()

    def predict(self):
        """
        Blocking (ie, not fast).
        """
        if not self.fact_extractor:
            return []
        labels = self.fact_extractor.predict(self.candidate_evidence)
        prediction = dict(zip(self.candidate_evidence, labels))
        prediction.update(self.labeled_evidence)
        return prediction

    # Instance attributes:
    # questions: A list of evidence
    # ranked_candidate_evidence: A dict candidate_evidence -> float

    #
    # "Private" methods
    #

    def load_all_evidence_from_database(self):
        self.all_evidence = []
        self.candidate_evidence = []
        self.labeled_evidence = {}
        for segment in self.relation._matching_text_segments():
            for e in segment.get_labeled_evidences(self.relation):
                self.all_evidence.append(e)
                if e.label == LabeledRelationEvidence.NORELATION:
                    self.labeled_evidence[e] = False
                elif e.label == LabeledRelationEvidence.YESRELATION:
                    self.labeled_evidence[e] = True
                else:
                    self.candidate_evidence.append(e)  # TODO: Check what happens with nonsense and such

    def train_fact_extractor(self):
        self.fact_extractor = FactExtractorFactory(defaults.extractor_config,
                                                   self.labeled_evidence)

    def rank_candidate_evidence(self):
        # TODO: Consider ranking only a smaller random sample of candidate_evidence for efficiency
        ranks = self.fact_extractor.decision_function(self.candidate_evidence)
        self.ranked_candidate_evidence = dict(zip(self.candidate_evidence, ranks))

    def choose_questions(self):
        # Criteria: Answer first candidates with decision function near 0
        # because they are the most uncertain for the classifier.
        self.questions = sorted(self.ranked_candidate_evidence,
                                key=lambda x: abs(self.ranked_candidate_evidence[x]))
