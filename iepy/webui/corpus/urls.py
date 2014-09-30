from django.conf.urls import patterns, url
from corpus import views
from corpus import api

urlpatterns = patterns(
    '',

    # Next item to label
    url(r'^next_segment_to_label/(?P<relation_id>\d+)/',
        views.next_segment_to_label,
        name='next_segment_to_label'),
    url(r'^next_document_to_label/(?P<relation_id>\d+)/',
        views.next_document_to_label,
        name='next_document_to_label'),

    # Navigate labeled items
    url(r'^navigate_labeled_segments/(?P<relation_id>\d+)/(?P<segment_id>\d+)/(?P<direction>\w+)/',
        views.navigate_labeled_segments,
        name='navigate_labeled_segments'),
    url(r'^navigate_labeled_documents/(?P<relation_id>\d+)/(?P<document_id>\d+)/(?P<direction>\w+)/',
        views.navigate_labeled_documents,
        name='navigate_labeled_documents'),

    # Labeling Forms & Views
    url(r'^label_evidence_for_segment/(?P<relation_id>\d+)/(?P<segment_id>\d+)/',
        views.LabelEvidenceOnSegmentView.as_view(),
        name='label_evidence_for_segment'),
    url(r'^label_evidence_for_document/(?P<relation_id>\d+)/(?P<document_id>\d+)/',
        views.LabelEvidenceOnDocumentView.as_view(),
        name='label_evidence_for_document'),

    # CRUD Angular EOs
    url(r'^crud/entity_occurrence/?$', api.EOCRUDView.as_view(), name='eo_crud_view'),
    url(r'^crud/text_segment/?$', api.SegmentCRUDView.as_view(), name='segm_crud_view'),
)
