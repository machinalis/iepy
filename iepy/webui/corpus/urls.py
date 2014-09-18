from django.conf.urls import patterns, url
from corpus import views

urlpatterns = patterns(
    '',
    url(r'^start_labeling_evidence/(?P<relation_id>\d+)', views.start_labeling_evidence,
        name='start_labeling_evidence'),
)
