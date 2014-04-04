from iepy.models import PreProcessSteps
from iepy.preprocess import BasePreProcessStepRunner


class CombinedNERRunner(BasePreProcessStepRunner):
    """A NER runner that is the combination of two different NER runners 
    (therefore, two different NERs). The entities returned by both NERs are 
    combined without any check, possibly leading to duplicate or overlapping 
    entities.
    """
    step = PreProcessSteps.ner

    def __init__(self, ner_runner1, ner_runner2, override=False):
        """The NER runners should be instances of BasePreProcessStepRunner.
        The override attributes of the NER runners are set to True, ignoring the
        previous values.
        The override parameter is used for both NER runners (overriding only one
        part is not allowed).
        """
        self.ner_runner1 = ner_runner1
        self.ner_runner2 = ner_runner2
        self.override = override

        # Do not allow overriding by parts
        self.ner_runner1.override = True
        self.ner_runner2.override = True

    def __call__(self, doc):
        if not self.override and doc.was_preprocess_done(PreProcessSteps.ner):
            # Already done
            return

        self.ner_runner1(doc)
        entities1 = doc.get_preprocess_result(PreProcessSteps.ner)

        self.ner_runner2(doc)
        entities2 = doc.get_preprocess_result(PreProcessSteps.ner)

        entities = merge_entities(entities1, entities2)
        doc.set_preprocess_result(PreProcessSteps.ner, entities)
        doc.save()


def merge_entities(entities1, entities2):
    return sorted(entities1 + entities2, key=lambda x: x.offset)

