from iepy.preprocess.pipeline import BasePreProcessStepRunner, PreProcessSteps
from collections import namedtuple

# Representation of Segments that a Segmenter found
RawSegment = namedtuple('RawSegment', 'offset offset_end entity_occurrences')


class SyntacticSegmenterRunner(BasePreProcessStepRunner):

    step = PreProcessSteps.segmentation

    def __init__(self, override=False, increment=True):
        self.override = override
        self.increment = increment

    def __call__(self, doc):
        was_done = doc.was_preprocess_step_done  # just a shortcut
        if not was_done(PreProcessSteps.ner) or not was_done(PreProcessSteps.sentencer):
            # preconditions not met.
            return
        if self.increment or self.override or not was_done(self.step):
            segments = self.build_syntactic_segments(doc)
            doc.set_segmentation_result(
                segments, override=self.override, increment=self.increment)
            doc.save()

    def build_syntactic_segments(self, doc):
        # Returns a list of RawSegments.
        # For sentence in the document with at least 2 Entity Occurrences,
        # a RawSegment is created
        result = []
        entity_occs = list(doc.get_entity_occurrences())
        eo_counter = 0
        L = len(doc.sentences)
        for i, start in enumerate(doc.sentences):
            end = doc.sentences[i + 1] if i + 1 < L else len(doc.tokens)
            # At this point, tokens[start:end] has a sentence
            # We need to check that it has at least 2 entities before
            # building a segment
            sentence_occurrences = []
            for eo_counter in range(eo_counter, len(entity_occs)):
                # Skip entities before start of sentence
                # If sentences are contiguous, and start at token 0,
                # this loop should never advance. But we don't know what the
                # sentencer does, so it's better to be careful
                if entity_occs[eo_counter].offset >= start:
                    break
            # Since "eo_counter" was over-used when iterating n previous for,
            # it will be updated with the last seen Entity Occurrence
            for eo_counter in range(eo_counter, len(entity_occs)):
                # Count entities inside the sentence
                eo = entity_occs[eo_counter]
                if eo.offset >= end or eo.offset_end > end:
                    # occurrence is not completely inside the sentence, then
                    # better to not consider it inside
                    break
                sentence_occurrences.append(eo)
            # Again, when leaving the for-loop, "eo_counter" was increased.
            # Given that sentences are already ordered, it's safe to to that
            if len(sentence_occurrences) >= 2:
                result.append(RawSegment(start, end, sentence_occurrences))
        return result
