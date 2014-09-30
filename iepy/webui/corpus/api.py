from djangular.views.crud import NgCRUDView
from corpus.models import EntityOccurrence, TextSegment


class EOCRUDView(NgCRUDView):
    model = EntityOccurrence
    fields = ['offset', 'offset_end']


class SegmentCRUDView(NgCRUDView):
    serializer_name = 'hydrated_python'
    model = TextSegment
    fields = ['offset', 'tokens']
