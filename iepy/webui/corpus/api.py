from django.forms.models import modelform_factory

from djangular.views.crud import NgCRUDView
from corpus.models import EntityOccurrence, TextSegment


class EOCRUDView(NgCRUDView):
    model = EntityOccurrence
    fields = ['offset', 'offset_end']

    def get_form_class(self):
        """
        Build ModelForm from model
        """
        return modelform_factory(self.model, fields=self.fields[:])


class SegmentCRUDView(NgCRUDView):
    serializer_name = 'hydrated_python'
    model = TextSegment
    fields = ['offset', 'tokens']
