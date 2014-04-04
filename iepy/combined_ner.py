from iepy.models import PreProcessSteps
from iepy.preprocess import BasePreProcessStepRunner


class CombinedNERRunner(BasePreProcessStepRunner):
    step = PreProcessSteps.nerc

    def __init__(self, ner_runner1, ner_runner2, override=False):
        self.ner_runner1 = ner_runner1
        self.ner_runner2 = ner_runner2
        self.override = override

        # Do not allow overriding by parts
        self.ner_runner1.override = True
        self.ner_runner2.override = True

    def __call__(self, doc):
        if not self.override and doc.was_preprocess_done(PreProcessSteps.nerc):
            #print 'Already done'
            return

        self.ner_runner1(doc)
        entities1 = doc.get_preprocess_result(PreProcessSteps.nerc)

        self.ner_runner2(doc)
        entities2 = doc.get_preprocess_result(PreProcessSteps.nerc)

        entities = merge_entities(entities1, entities2)
        doc.set_preprocess_result(PreProcessSteps.nerc, entities)
        doc.save()


def merge_entities(entities1, entities2):
    return sorted(entities1 + entities2, key=lambda x: x.offset)

