from iepy.models import PreProcessSteps
from iepy.preprocess import BasePreProcessStepRunner


class CombinedNERRunner(BasePreProcessStepRunner):
    """A NER runner that is the combination of different NER runners
    (therefore, different NERs).
    The entities returned by each NERs are combined by method merge_entities
    without any check, possibly leading to duplicate or overlapping entities;
    but subclassing this combiner you may define something different.
    """
    step = PreProcessSteps.ner

    def __init__(self, ners, override=False):
        """The NER runners should be instances of BasePreProcessStepRunner.
        The override attributes of each NER runner is set to True, ignoring the
        previous values.
        The override parameter is used for all NER runners (overriding only one
        part is not allowed).
        """
        if not ners:
            raise ValueError(u'Empty ners to combine')
        self.ners = ners
        self.override = override

        # Do not allow overriding by parts
        for sub_ner in self.ners:
            sub_ner.override = True

    def merge_entities(self, sub_results):
        # Default merger does nothing but merging & sorting by offset
        all_entities = []
        for ner, sub_entities in sub_results:
            all_entities.extend(sub_entities)
        return sorted(all_entities, key=lambda x: x.offset)

    def __call__(self, doc):
        if not self.override and doc.was_preprocess_done(PreProcessSteps.ner):
            # Already done
            return

        sub_results = []
        for sub_ner in self.ners:
            sub_ner(doc)
            sub_results.append(
                (sub_ner, doc.get_preprocess_result(PreProcessSteps.ner))
            )

        entities = self.merge_entities(sub_results)
        doc.set_preprocess_result(PreProcessSteps.ner, entities)
        doc.save()


class KindPreferenceCombinedNERRunner(CombinedNERRunner):
    """
    Similar to the CombinedNERRunner, but when merging results from different
    taggers avoids overlapping by discarding those entities whose kind was worst
    ranked on the Combiner creation.
    If a given entity kind is not ranked on Combiner, will be treated worst than
    the worst ranked.
    If conflict remains, following rules apply:
        - shorter occurrences are preferred over larger
        - occurrences of former sub NERs are preferred.
    """
    def __init__(self, ners, override=False, rank=tuple()):
        """
        """
        # the lower the rank, the more important
        self.kinds_rank = dict((k, i) for i, k in enumerate(rank))
        self.worst_rank = len(self.kinds_rank)
        super(KindPreferenceCombinedNERRunner, self).__init__(ners, override)

    def get_rank(self, entityocc):
        return self.kinds_rank.setdefault(entityocc.entity.kind, self.worst_rank)

    def merge_entities(self, sub_results):
        sorted_occurrences = super(KindPreferenceCombinedNERRunner,
                                   self).merge_entities(sub_results)
        prev = sorted_occurrences[0]
        to_remove = set()
        # given that entities are sorted, cannot be the case that one entity
        # has offset lower than the previous one
        for eo in sorted_occurrences[1:]:
            if eo.offset < prev.offset_end:
                # there's an overlap. One of these 2 must be removed
                prev_criteria = (
                    self.get_rank(prev),  # kind rank
                    -1 * (prev.offset_end - prev.offset)  # inversed length
                )
                eo_criteria = (
                    self.get_rank(eo),
                    -1 * (eo.offset_end - eo.offset)
                )
                if prev_criteria <= eo_criteria:
                    to_remove.add(eo)
                else:
                    to_remove.add(prev)
                    prev = eo
            else:
                prev = eo
        return [eo_i for eo_i in sorted_occurrences if eo_i not in to_remove]


