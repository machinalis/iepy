from djangular.views.crud import NgCRUDView
from corpus.models import EntityOccurrence


class EOCRUDView(NgCRUDView):
    model = EntityOccurrence
