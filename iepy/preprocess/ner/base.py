from collections import namedtuple
from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps


FoundEntity = namedtuple('FoundEntity', 'key kind_name alias offset offset_end from_gazette')


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

    def __call__(self, doc):
        # Do not override this method when subclassing. Instead,
        # do it on the "run_ner"
        if not self.ok_for_running(doc):
            return
        entities = self.run_ner(doc)
        doc.set_ner_result(entities)
        doc.save()

    def run_ner(self, doc):
        # Define logic in here
        return []

    def build_occurrence(self, key, kind_name, alias, offset, offset_end):
        return FoundEntity(key, kind_name.upper(), alias, offset, offset_end, False)
