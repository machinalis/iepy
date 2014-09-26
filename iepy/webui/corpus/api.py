from djangular.views.crud import NGCrudView
from corpus.models import EntityOccurrence


class EOCRUDView(NGCrudView):
    model = EntityOccurrence
