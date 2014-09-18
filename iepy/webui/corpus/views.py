from django.shortcuts import get_object_or_404, render_to_response, redirect

from corpus.models import Relation


def start_labeling_evidence(request, relation_id):
    relation = get_object_or_404(Relation, pk=relation_id)
    segment = relation.get_next_segment_to_label()
    if segment is None:
        return render_to_response('message.html',
                                  {'msg': 'There are no more evidence to label'})
    return redirect('label_evidence_for_segment', segment.pk)
    #return render_to_response('label_evidence.html',
    #                          {'title': 'hello world'})


#def show_and_process_questions_for_segment(request, relation_id, segment_id):
#    pass
