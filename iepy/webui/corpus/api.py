from django.contrib.auth.decorators import login_required
from django.forms.models import modelform_factory
from django.utils.decorators import method_decorator

from djangular.views.crud import NgCRUDView
from corpus.models import EntityOccurrence, Entity


class LoginNgCrudView(NgCRUDView):
    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class EOCRUDView(LoginNgCrudView):
    serializer_name = 'underscore_resolution'
    model = EntityOccurrence
    fields = ['offset', 'offset_end', 'entity', 'entity__kind__name']

    def get_form_class(self):
        """
        Build ModelForm from model
        """
        fields = [x for x in self.fields if not x.count("__")]
        return modelform_factory(self.model, fields=fields)


class EntityCRUDView(LoginNgCrudView):
    model = Entity
