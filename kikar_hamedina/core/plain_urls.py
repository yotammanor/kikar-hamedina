from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import plain_views
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag

urlpatterns = patterns('',
    url(r'^$', plain_views.HomeView.as_view(),
        kwargs={'context_object': 'index'},
        name='plain-index'),
    url(r'^untagged/$', plain_views.HomeView.as_view(
        queryset=Facebook_Status.objects.filter(tags=None).order_by('published')),
        kwargs={'context_object': 'untagged'},
        name='plain-untagged'),
    url(r'^add-tag/(?P<id>\d+)/$', plain_views.add_tag,
        name='add-tag'),
    url(r'^party/(?P<id>\d+)/$', plain_views.PartyView.as_view(),
        kwargs={'variable_column': 'feed__person__party__id',
                'context_object': 'party'},
        name='plain-party'),
    url(r'^person/(?P<id>\d+)/$', plain_views.PersonView.as_view(),
        kwargs={'variable_column': 'feed__person__id',
                'context_object': 'person'},
        name='plain-person'),
    # url(r'^tag/id/(?P<id>\d+)/$', plain_views.StatusFilterView.as_view(),
    # kwargs={'variable_column': 'tags__id'}, name='plain-tag-id'),
    url(r'^tag/(?P<search_field>\w+)/(?P<id>\w+)/$', plain_views.TagView.as_view(),
        kwargs={'variable_column': 'tags',
                'context_object': 'tag'},
        name='plain-tag'),

)

urlpatterns = format_suffix_patterns(urlpatterns)

