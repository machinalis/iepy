import logging
from enum import Enum

logger = logging.getLogger(__name__)


class PreProcessSteps(Enum):
    # numbers do not imply order
    tokenization = 1
    lemmatization = 6
    sentencer = 2
    tagging = 3
    ner = 4
    segmentation = 5
    syntactic_parsing = 7


class PreProcessPipeline(object):
    """Coordinates the pre-processing tasks on a set of documents"""

    def __init__(self, step_runners, documents_manager):
        """Takes a list of callables and a documents-manager.

            Step Runners may be any callable. It they have an attribute step,
            then that runner will be treated as the responsible for
            accomplishing such a PreProcessStep.
        """
        from iepy.data.db import DocumentManager  # circular imports safety
        self.step_runners = step_runners
        if not isinstance(documents_manager, DocumentManager):
            documents_manager = DocumentManager(documents_manager)
        self.documents = documents_manager

    def walk_document(self, doc):
        """Computes all the missing pre-process steps for the given document"""
        for step in self.step_runners:
            step(doc)
        return

    def process_step_in_batch(self, runner):
        """Tries to apply the required step to all documents lacking it"""
        logger.info('Starting preprocessing step %s', runner)
        if hasattr(runner, 'step') and not (runner.override or runner.increment):
            docs = self.documents.get_documents_lacking_preprocess(runner.step)
        else:
            docs = self.documents  # everything
        for i, doc in enumerate(docs):
            runner(doc)
            logger.info('\tDone for %i documents', i + 1)

    def process_everything(self):
        """Tries to apply all the steps to all documents"""
        for runner in self.step_runners:
            self.process_step_in_batch(runner)


class BasePreProcessStepRunner(object):
    # If it's for a particular step, you can write
    # step = PreProcessSteps.something

    def __init__(self, override=False, increment=False):
        self.override = override
        self.increment = increment

    def __call__(self, doc):
        # You'll have to:
        # - Check if the document satisfies pre-conditions, and if not, do nothing
        # - Explicitely store pre process results on the document
        # - Based on the "override" paramenter, and on your checks to see if the step
        #   was already done or not, decide if you will
        #    - skip
        #    - re-do step.
        raise NotImplementedError
