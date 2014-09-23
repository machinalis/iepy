from django.conf.urls import patterns, url
from corpus import views

urlpatterns = patterns(
    '',
    url(r'^start_labeling_evidence/(?P<relation_id>\d+)/',
        views.start_labeling_evidence,
        name='start_labeling_evidence'),
    url(r'^label_evidence_for_segment/(?P<relation_id>\d+)/(?P<segment_id>\d+)/',
        views.LabelEvidenceOnSegmentView.as_view(),
        name='label_evidence_for_segment'),
    url(r'^navigate_labeled_segments/(?P<relation_id>\d+)/(?P<segment_id>\d+)/(?P<direction>\w+)',
        views.navigate_labeled_segments,
        name='navigate_labeled_segments'),
)
