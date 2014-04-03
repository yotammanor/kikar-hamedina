from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import plain_views
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag

urlpatterns = patterns('',
                       url(r'^$', plain_views.HomepageView.as_view(), name='plain-index'),
                       url(r'^all-statuses/$', plain_views.AllStatusesView.as_view(queryset=Facebook_Status.objects.order_by('-published')),
                           kwargs={'context_object': 'index'},
                           name='plain-all-statuses'),
                       url(r'^untagged/$', plain_views.AllStatusesView.as_view(
                           queryset=Facebook_Status.objects.filter(tags=None).order_by('-published')),
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
                       url(r'^tag/(?P<search_field>\w+)/(?P<id>[\w\s]+)/$', plain_views.TagView.as_view(),
                           kwargs={'variable_column': 'tags',
                                   'context_object': 'tag'},
                           name='plain-tag'),
                       url(r'^search/$', plain_views.SearchView.as_view(),
                           kwargs={'variable_column': 'content', 'context_object': 'search'}, name='plain-search'),
                       url(r'^persons/$', plain_views.AllPersons.as_view(queryset=Person.objects.all()),
                           name='all-persons'),
                       url(r'^parties/$', plain_views.AllParties.as_view(queryset=Party.objects.all()),
                           name='all-parties'),
                       url(r'^tags/$', plain_views.AllTags.as_view(queryset=Tag.objects.all()),
                           name='all-tags'),
                       url(r'^about/$', plain_views.about_page, name='about',),

                       url(r'^status_update/(?P<status_id>\w+)/$',plain_views.status_update),
                       url(r'^search_bar/$',plain_views.search_bar)
                       # url(r'^search/(?P<id>[\w\s]+)/$', plain_views.SearchView.as_view(),
                       #     kwargs={'variable_column': 'content',
                       #             'context_object': 'search'},
                       #     name='plain-search'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

