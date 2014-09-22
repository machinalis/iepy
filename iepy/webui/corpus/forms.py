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
        if instance and instance.label is None:
            # When created, LabeledRelationEvidence get None as label.
            # For such cases, on forms, we'll suggest the model.default
            instance.label = DEFAULT_LABEL
        super().__init__(*args, **kwargs)
        self.fields['label'].label = ''

    def has_changed(self, *args, **kwargs):
        changed = super().has_changed(*args, **kwargs)
        if not changed and self.instance.label == DEFAULT_LABEL:
            # On init we "hacked" the instance so the form was created showing our
            # desired default value. Because of that, we may not be seeing that change.
            # The worst can happen by returning True is some unneeded save. Not bad.
            return True
        return changed
