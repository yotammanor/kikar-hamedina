from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views, api

urlpatterns = patterns('',
    url(r'^persons/$', api.PersonsList.as_view(), name='person-list'),
    url(r'^persons/(?P<pk>[0-9]+)/$', api.PersonDetail.as_view(), name='person-detail'),
    url(r'^parties/$', api.PartiesList.as_view(), name='party-list'),
    url(r'^parties/(?P<pk>[0-9]+)/$', api.PartyDetail.as_view(), name='party-detail'),
    url(r'^statuses/$', api.StatusList.as_view(), name='status-list'),
    url(r'^feeds/$', api.FeedList.as_view(), name='feed-list'),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^$', views.index, name='index'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

