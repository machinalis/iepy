from iepy.models import PreProcessSteps


class PreProcessPipeline(object):

    def __init__(self, step_runners, documents):
        self.step_runners = step_runners
        self.documents = documents

    def walk_document(self, doc):
        """Computes all the missing pre-process steps for the given document"""
        for step in self.step_runners():
            step(doc)
        return

    def process_step_in_batch(self, step):
        """Tries to apply the required step to all documents lacking it"""
        for doc in self.documents.get_documents_lacking_preprocess(step):
            step.apply(doc)

    def process_everything(self):
        """Tries to apply all the steps to all documents"""
        for step in self.step_runners():
            self.process_step_in_batch(step)


class BasePreProcessStepRunner(object):

    def __init__(self, step):
        if not isinstance(step, PreProcessSteps):
            raise ValueError()
        self.step = step

    def __call__(self, doc):
        # You'll have to:
        # - check if the document satisfies pre-conditions
        # - decide what to do if the document had that sted already done:
        #    - skip?
        #    - re-doit?
        #    - raise?
        # - store pre process results on the document
        raise NotImplementedError
