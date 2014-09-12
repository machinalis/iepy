from iepy.preprocess.ner.base import BaseNERRunner


class CombinedNERRunner(BaseNERRunner):
    """A NER runner that is the combination of different NER runners
    (therefore, different NERs).

    The entities returned by each NER are combined by the method merge_entities
    without any check, possibly leading to duplicate or overlapping entities;
    but subclassing this combiner you may define something different.
    """

    def __init__(self, ners, override=False):
        """The NER runners should be instances of BasePreProcessStepRunner.
        Notes:
            - Each of the sub-ners will be configured to run with override-mode
            "on", no matter what is the global override value.
            The global override, will be used for determining wether to start
            or not the global-combined process.
            - Overriding only some NERs and not others is not allowed.
        """
        super(CombinedNERRunner, self).__init__(override=override)
        if not ners:
            raise ValueError(u'Empty NERs to combine')
        self.ners = ners

        for sub_ner in self.ners:
            sub_ner.override = True

    def merge_entities(self, sub_results):
        # Default merger does nothing but merging & sorting by offset
        all_entities = []
        for ner, sub_entities in sub_results:
            all_entities.extend(sub_entities)
        return sorted(all_entities, key=lambda x: x.offset)

    def run_ner(self, doc):
        sub_results = []
        for sub_ner in self.ners:
            sub_results.append(
                (sub_ner,
                 sub_ner.run_ner(doc)
                 )
            )
        return self.merge_entities(sub_results)


class NoOverlapCombinedNERRunner(CombinedNERRunner):
    """
    Similar to the CombinedNERRunner, but when merging results from different
    taggers avoids overlapping by discarding those entities that were provided
    by later subners.

    It's assumed that each sub NER provides non overlapped entities.
    """
    def overlapped_entities(self, e1, e2):
        min1, max1 = e1.offset, e1.offset_end
        min2, max2 = e2.offset, e2.offset_end
        return bool(max(0, min(max1, max2) - max(min1, min2)))

    def merge_entities(self, sub_results):
        result = []
        for ner, sub_res in sub_results:
            if not result:
                # first ner returning something. all in.
                result.extend(sub_res)
            else:
                for ent in sub_res:
                    if any(self.overlapped_entities(ent, e_i) for e_i in result):
                        continue
                    result.append(ent)
        return sorted(result, key=lambda x: x.offset)


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
        if not isinstance(rank, (tuple, list)):
            raise ValueError(u'rank can only be a list or tuple')
        self.kinds_rank = dict((k, i) for i, k in enumerate(rank))
        self.worst_rank = len(self.kinds_rank)
        super(KindPreferenceCombinedNERRunner, self).__init__(ners, override)

    def get_rank(self, found_entity):
        return self.kinds_rank.setdefault(found_entity.kind_name, self.worst_rank)

    def merge_entities(self, sub_results):
        sorted_occurrences = super(KindPreferenceCombinedNERRunner,
                                   self).merge_entities(sub_results)
        if not sorted_occurrences:
            return sorted_occurrences
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
