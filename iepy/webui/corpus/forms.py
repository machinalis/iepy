# -*- coding: utf-8 -*-
from django import forms

from corpus.models import EvidenceLabel

DEFAULT_LABEL = EvidenceLabel._meta.get_field('label').default


class EvidenceForm(forms.ModelForm):
    class Meta:
        model = EvidenceLabel
        fields = ["label"]
        widgets = {
            'label': forms.RadioSelect
        }

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        restore_None = False
        if instance and instance.label is None:
            # When created, EvidenceLabel get None as label.
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
            if EvidenceLabel.objects.get(pk=self.instance.pk).label is None:
                changed = True
        return changed


class EvidenceOnDocumentForm(EvidenceForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f_lbl = self.fields['label']
        f_lbl.widget = forms.HiddenInput()
        # "forms" is the name of some Angular context object on the frontend.
        f_lbl.widget.attrs['ng-value'] = 'forms["%s"]' % self.prefix
        f_lbl.required = False


class EvidenceToolboxForm(EvidenceForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        f_lbl = self.fields['label']
        prev_widget = f_lbl
        f_lbl.widget = forms.RadioSelect(choices=prev_widget.choices)
        f_lbl.widget.attrs['ng-model'] = 'current_tool'
