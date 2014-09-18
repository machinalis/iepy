from django.shortcuts import get_object_or_404, render_to_response

from corpus.models import Relation


def start_labeling_evidence(request, relation_id):
    #relation = get_object_or_404(Relation, pk=relation_id)
    #s = pick_segment()
    #redirect(show_and_process_questions_for_segment(rea, s))
    return render_to_response('label_evidence.html',
                              {'title': 'hello world'})


#def show_and_process_questions_for_segment(request, relation_id, segment_id):
#    pass
