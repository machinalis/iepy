from django.shortcuts import get_object_or_404, render_to_response, redirect

from corpus import forms
from corpus.models import Relation, TextSegment


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
    return render_to_response('corpus/segment_questions.html', context)
