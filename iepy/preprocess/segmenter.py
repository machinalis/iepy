from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps


class SyntacticSegmenterRunner(BasePreProcessStepRunner):

    step = PreProcessSteps.segmentation

    def __init__(self, override=False):
        self.override = override

    def __call__(self, doc):
        if not doc.was_preprocess_step_done(PreProcessSteps.ner) or not doc.was_preprocess_done(PreProcessSteps.sentencer):
            return
        if self.override or not doc.was_preprocess_done(self.step):
            assert all(doc.entities[i].offset <= doc.entities[i + 1].offset for i in range(len(doc.entities) - 1))
            doc.clear_segments()
            doc.build_syntactic_segments()
            doc.flag_preprocess_done(self.step)
            doc.save()
