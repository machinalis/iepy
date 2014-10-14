import random
import logging

from iepy import defaults
from iepy.extraction.fact_extractor import FactExtractorFactory


logger = logging.getLogger(__name__)


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

    def __init__(self, relation, labeled_evidences):
        self.relation = relation
        self.fact_extractor = None
        self._setup_labeled_evidences(labeled_evidences)
        self.questions = list(self.candidate_evidence)

    def start(self):
        """
        Blocking.
        """
        pass

    def add_answer(self, evidence, answer):
        """
        Not blocking.
        """
        assert answer in (True, False)
        self.labeled_evidence[evidence] = answer
        for list_ in (self.questions, self.candidate_evidence):  # TODO: Check performance. Should use set?
            list_.remove(evidence)
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

    def _setup_labeled_evidences(self, labeled_evidences):
        self.candidate_evidence = []
        self.labeled_evidence = {}
        for e, lbl in labeled_evidences.items():
            if lbl is None:
                self.candidate_evidence.append(e)
            else:
                self.labeled_evidence[e] = lbl
        if not self.candidate_evidence:
            raise ValueError("Cannot start core without candidate evidence")
        logger.info("Loaded {} candidate evidence and {} labeled evidence".format(
                    len(self.candidate_evidence), len(self.labeled_evidence)))

    def train_fact_extractor(self):
        self.fact_extractor = FactExtractorFactory(defaults.extractor_config,
                                                   self.labeled_evidence)

    def rank_candidate_evidence(self):
        N = 100
        logger.info("Ranking a sample of {} candidate evidence".format(N))
        sample = random.sample(self.candidate_evidence, N)
        ranks = self.fact_extractor.decision_function(sample)
        self.ranked_candidate_evidence = dict(zip(self.candidate_evidence, ranks))
        ranks = [abs(x) for x in ranks]
        logger.debug("Ranking completed, lowest absolute rank={}, "
                     "highest absolute rank={}".format(min(ranks), max(ranks)))

    def choose_questions(self):
        # Criteria: Answer first candidates with decision function near 0
        # because they are the most uncertain for the classifier.
        self.questions = sorted(self.ranked_candidate_evidence,
                                key=lambda x: abs(self.ranked_candidate_evidence[x]))
