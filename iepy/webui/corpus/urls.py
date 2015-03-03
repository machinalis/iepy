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
    url(r'^navigate_labeled_segments/(?P<relation_id>\d+)/(?P<segment_id>\d+)/(?P<direction>\w+)/judgeless',
        views.navigate_labeled_segments,
        kwargs={"judgeless": True},
        name='navigate_labeled_segments_judgeless'),
    url(r'^navigate_labeled_documents/(?P<relation_id>\d+)/(?P<document_id>\d+)/(?P<direction>\w+)/judgeless',
        views.navigate_labeled_documents,
        kwargs={"judgeless": True},
        name='navigate_labeled_documents_judgeless'),
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

    # Human in the loop
    url(r'^human_in_the_loop/(?P<relation_id>\d+)/(?P<segment_id>\d+)/',
        views.HumanInTheLoopView.as_view(),
        name='human_in_the_loop_segment'),
    url(r'^human_in_the_loop/(?P<relation_id>\d+)/',
        views.human_in_the_loop,
        name='human_in_the_loop'),

    # Document navigation
    url(r'^navigate_documents/(?P<document_id>\d+)/(?P<direction>\w+)/',
        views.navigate_documents,
        name='navigate_documents'),
    url(r'^navigate_document/(?P<document_id>\d+)/',
        views.DocumentNavigation.as_view(),
        name='navigate_document'),

    # CRUD Angular EOs
    url(r'^crud/entity_occurrence/?$', api.EOCRUDView.as_view(), name='eo_crud_view'),
    url(r'^crud/entity/?$', api.EntityCRUDView.as_view(), name='entity_crud_view'),

    url(r'^create_eo/?$', views.create_entity_occurrence, name='create_entity_occurrence'),
)
