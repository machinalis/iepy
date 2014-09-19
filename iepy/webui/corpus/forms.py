# -*- coding: utf-8 -*-

from django import forms

from corpus.models import LabeledRelationEvidence


class LabeledRelationEvidenceForm(forms.ModelForm):
    class Meta:
        model = LabeledRelationEvidence
        fields = ["label"]
