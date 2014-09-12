from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps


class BaseNERRunner(BasePreProcessStepRunner):
    """Base class for defining NER runners"""
    step = PreProcessSteps.ner

    def __init__(self, override=False):
        self.override = override

    def ok_for_running(self, doc):
        if not doc.was_preprocess_step_done(PreProcessSteps.sentencer):
            # Doc needs previous preprocess steps to be done
            return False
        if not self.override and doc.was_preprocess_step_done(self.step):
            # Current step was already done, and not working in override mode
            return False
        return True
