from django.contrib import messages
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render_to_response, render, redirect

from extra_views import ModelFormSetView

from corpus import forms
from corpus.models import Relation, TextSegment, LabeledRelationEvidence
from corpus.forms import EvidenceForm


def start_labeling_evidence(request, relation_id):
    relation = get_object_or_404(Relation, pk=relation_id)
    segment = relation.get_next_segment_to_label()
    if segment is None:
        return render_to_response('message.html',
                                  {'msg': 'There are no more evidence to label'})
    return redirect('corpus:label_evidence_for_segment', relation.pk, segment.pk)


def label_evidence_for_segment(request, relation_id, segment_id):
    segment = get_object_or_404(TextSegment, pk=segment_id)
    relation = get_object_or_404(Relation, pk=relation_id)
    segment.hydrate()

    evidence_forms = []
    for evidence in segment.get_labeled_evidences(relation):
        form = forms.LabeledRelationEvidenceForm(instance=evidence)
        evidence_forms.append(form)

    form_select = """
        <select id="id_label" name="label">
        <option value="NO">No relation present</option>
        <option value="YE">Yes, relation is present</option>
        <option value="DK">Don't know if the relation is present</option>
        <option value="SK" selected="selected">Skipped labeling of this evidence</option>
        <option value="NS">Evidence is nonsense</option>
        </select>
    """

    title = "You're gonna answer questions for segment " \
            "'{0}' respect relation '{1}'".format(segment, relation)
    context = {
        "title": title,
        "segment": segment,
        "relation": relation,
        "questions": [
            {
                "left_occurrence": {"name": "Embolism", "id": 1},
                "right_occurrence": {"name": "Brain damage", "id": 2},
                "options": form_select
            },
            {
                "left_occurrence": {"name": "Baby", "id": 3},
                "right_occurrence": {"name": "Brain damage", "id": 2},
                "options": form_select
            },
        ]
    }
    return render(request, 'corpus/segment_questions.html', context)


class LabelEvidenceOnSegmentView(ModelFormSetView):
    template_name = 'corpus/segment_questions.html'
    form_class = EvidenceForm
    model = LabeledRelationEvidence
    extra = 0
    max_num = None
    can_order = False
    can_delete = False

    def get_context_data(self, **kwargs):
        ctx = super(LabelEvidenceOnSegmentView, self).get_context_data(**kwargs)
        self.segment.hydrate()
        title = "Labeling Evidence for Relation {0}".format(self.relation)
        subtitle = 'For Document "{0}", Text Segment id {1}'.format(
            self.segment.document.human_identifier,
            self.segment.id)

        ctx.update({
            'title': title,
            'subtitle': subtitle,
            'segment': self.segment,
            'segment_rich_tokens': list(self.segment.get_enriched_tokens()),
            'relation': self.relation
        })
        return ctx

    def get_segment_and_relation(self):
        if hasattr(self, 'segment') and hasattr(self, 'relation'):
            return self.segment, self.relation
        self.segment = get_object_or_404(TextSegment, pk=self.kwargs['segment_id'])
        self.segment.hydrate()
        self.relation = get_object_or_404(Relation, pk=self.kwargs['relation_id'])
        self.evidences = list(self.segment.get_labeled_evidences(self.relation))
        return self.segment, self.relation

    def get_queryset(self):
        segment, relation = self.get_segment_and_relation()
        return super().get_queryset().filter(
            segment=self.segment, relation=self.relation
        )

    def get_success_url(self):
        return reverse('corpus:start_labeling_evidence', args=[self.relation.pk])

    def formset_valid(self, formset):
        """
        If the formset is valid redirect to the supplied URL
        """
        messages.add_message(self.request, messages.INFO,
                             'Changes saved for segment {0}.'.format(self.segment.id))
        return super().formset_valid(formset)
