from djangular.views.crud import NgCRUDView
from corpus.models import EntityOccurrence, TextSegment


class EOCRUDView(NgCRUDView):
    model = EntityOccurrence


class SegmentCRUDView(NgCRUDView):
    model = TextSegment
