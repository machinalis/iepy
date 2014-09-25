# -*- coding: utf-8 -*-
from django import forms

from corpus.models import LabeledRelationEvidence

DEFAULT_LABEL = LabeledRelationEvidence._meta.get_field('label').default


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = LabeledRelationEvidence
        fields = ["label"]

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        restore_None = False
        if instance and instance.label is None:
            # When created, LabeledRelationEvidence get None as label.
            # For such cases, on forms, we'll suggest the model.default
            instance.label = DEFAULT_LABEL
            restore_None = True
        super().__init__(*args, **kwargs)
        if restore_None:
            self.instance.label = None
        self.fields['label'].label = ''

    def has_changed(self, *args, **kwargs):
        changed = super().has_changed(*args, **kwargs)
        if not changed and self.instance.label == DEFAULT_LABEL:
            # On init we "hacked" the instance so the form was created showing our
            # desired default value. Because of that, we may not be seeing that change.
            if LabeledRelationEvidence.objects.get(pk=self.instance.pk).label is None:
                changed = True
        return changed

    def setup_for_angular(self, hidden=True):
        self.fields['label'].widget = forms.TextInput()  # .HiddenInput()
        w = self.fields['label'].widget
        w.attrs['ng-value'] = 'forms["%s"]' % self.prefix
