from django.conf.urls import patterns, url
from corpus import views

urlpatterns = patterns(
    '',
    url(r'^next_segment_to_label/(?P<relation_id>\d+)/',
        views.next_segment_to_label,
        name='next_segment_to_label'),
    url(r'^next_document_to_label/(?P<relation_id>\d+)/',
        views.next_document_to_label,
        name='next_document_to_label'),
    url(r'^label_evidence_for_segment/(?P<relation_id>\d+)/(?P<segment_id>\d+)/',
        views.LabelEvidenceOnSegmentView.as_view(),
        name='label_evidence_for_segment'),
    url(r'^navigate_labeled_segments/(?P<relation_id>\d+)/(?P<segment_id>\d+)/(?P<direction>\w+)',
        views.navigate_labeled_segments,
        name='navigate_labeled_segments'),
    url(r'^label_evidence_for_document/(?P<relation_id>\d+)/(?P<document_id>\d+)',
        views.LabelEvidenceOnDocumentView.as_view(),
        name='label_evidence_for_document'),
)
