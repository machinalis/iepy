from django.contrib.auth.decorators import login_required
from django.forms.models import modelform_factory
from django.utils.decorators import method_decorator

from djangular.views.crud import NgCRUDView
from corpus.models import EntityOccurrence, TextSegment


class LoginNgCrudView(NgCRUDView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class EOCRUDView(LoginNgCrudView):
    model = EntityOccurrence
    fields = ['offset', 'offset_end', 'entity', 'milanesa']

    def get_form_class(self):
        """
        Build ModelForm from model
        """
        return modelform_factory(self.model, fields=self.fields[:])


class SegmentCRUDView(LoginNgCrudView):
    serializer_name = 'hydrated_python'
    model = TextSegment
    fields = ['offset', 'tokens']
