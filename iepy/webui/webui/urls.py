from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',
    # Home page
    url(r'^$', "corpus.views.home", name='home'),

    url(r'^admin/', include(admin.site.urls)),
    url(r'^corpus/', include('corpus.urls', namespace='corpus')),
)
