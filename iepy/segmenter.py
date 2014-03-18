from iepy.models import PreProcessSteps, TextSegment
from iepy.preprocess import BasePreProcessStepRunner


class SyntacticSegmenterRunner(BasePreProcessStepRunner):

    step = PreProcessSteps.segmentation

    def __call__(self, doc):
        entity = 0
        L = len(doc.sentences)
        for i, start in enumerate(doc.sentences):
            end = doc.sentences[i + 1] if i + 1 < L else len(doc.tokens)
            # At this point, tokens[start:end] has a sentence
            # We need to check that it has at least 2 entities before
            # building a segment
            n = 0
            for entity in xrange(entity, len(doc.entities)):
                # Skip entities before start of sentence
                # If sentences are contiguous, and start at token 0,
                # this loop should never advance. But we don't know what the
                # sentencer does, so it's ebtter to be careful
                if doc.entities[entity].offset >= start:
                    break
            for entity in xrange(entity, len(doc.entities)):
                # Count entities inside the sentence
                if doc.entities[entity].offset >= end:
                    break
                n += 1
            if n >= 2:
                s = TextSegment.build(doc, start, end)
                s.save()
# FIXME: handling doing this two times?
# FIXME: set document status properly


class ContextualSegmenterRunner(BasePreProcessStepRunner):

    step = PreProcessSteps.segmentation

    def __init__(self, distance):
        self.distance = distance

    def __call__(self, doc):
        """
        Build all contextual text segments in a contextual way. A context is a
        contiguous piece of the document with at least 2 tokens separated by
        a distance of no more than 'd'.

        - A candidate segment should be built around each entity,
        with k tokens ahead and behind.
        - If an nearby entity is found, extend another k tokens (only once, do
        not iterate this step).
        - If no entities are found around the "center" entity, ignore this segment
        - multi-token entities should always be captured together
        - if two segments overlap, keep the larger one
        """
        L = len(doc.entities)
        d = self.distance
        i = 0
        lstart, lend = -1, -1
        while i + 1 < L:
            # Find 2 entities that are "close"
            left, middle = doc.entities[i:i + 2]
            while middle.offset - left.offset_end >= d:
                i += 1
                if i + 1 == L:
                    # we're done!
                    return
                left, middle = doc.entities[i:i + 2]
            # Find the rightmost in the segment
            if i + 2 < L and doc.entities[i + 2].offset - middle.offset_end < d:
                right = doc.entities[i + 2]
            else:
                right = middle
            # Calculate the starting/ending offsets
            start = max(0, left.offset - d)
            end = min(right.offset_end + d, len(doc.tokens))
            # Make sure that this doesn't split a token:
            j = i
            while j >= 0 and doc.entities[j].offset_end > start:
                start = min(start, doc.entities[j].offset)
                j -= 1
            j = i
            while j < L and doc.entities[j].offset < end:
                end = max(end, doc.entities[j].offset_end)
                j += 1
            if not (end == lend and start >= lstart):
                # Not a repeat
                s = TextSegment.build(doc, start, end)
                s.save()
            lstart, lend = start, end
            i += 1

# FIXME: handling doing this two times?
# FIXME: set document status properly

