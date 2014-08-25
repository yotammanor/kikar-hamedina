from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import views
from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag
from mks.models import Party, Member
from django.conf import settings
from tastypie.api import Api
from api import *
from insights import StatsMemberResource, StatsPartyResource


v1_api = Api(api_name='v1')
v1_api.register(MemberResource())
v1_api.register(PartyResource())
v1_api.register(KnessetResource())
v1_api.register(Facebook_StatusResource())
v1_api.register(Facebook_FeedResource())
v1_api.register(TagResource())
v1_api.register(StatsMemberResource())
v1_api.register(StatsPartyResource())

urlpatterns = patterns('',
                       # homepage
                       url(r'^$', views.HomepageView.as_view(), name='index'),
                       # include urls
                       url(r'^api/', include(v1_api.urls)),
                       url(r'^search-solr/', include('haystack.urls')),
                       # navbar direct decendants url
                       url(r'^billboards/$', views.BillboardsView.as_view(), name='billboards'),
                       # TODO: rename to `hot` to covr hot topics
                       url(r'^hot-topics/$', views.HotTopicsView.as_view(), name='hot-topics'),
                       url(r'^searchgui/$', views.SearchGuiView.as_view(), name="search-gui"),
                       url(r'^about/$', views.about_page, name='about', ),
                       url(r'^all-statuses/$',
                           views.AllStatusesView.as_view(queryset=Facebook_Status.objects.order_by('-published')),
                           kwargs={'context_object': 'index'},
                           name='all-statuses'),
                       url(r'^search_bar/$', views.search_bar),
                       # main status filter-views in website
                       url(r'^party/(?P<id>\d+)/$', views.PartyView.as_view(),
                           kwargs={'variable_column': 'feed__person__party__id',  # TODO: refactor!
                                   'context_object': 'party'},
                           name='party'),
                       url(r'^member/(?P<id>\d+)/$', views.MemberView.as_view(),
                           kwargs={'variable_column': 'feed__persona__object_id',
                                   'context_object': 'member'},
                           name='member'),
                       url(r'^tag/(?P<search_field>\w+)/(?P<id>[\w\s\-:"\'!\?&\.#]+)/$', views.TagView.as_view(),
                           kwargs={'variable_column': 'tags',
                                   'context_object': 'tag'},
                           name='tag'),
                       url(r'^search/$', views.SearchView.as_view(),
                           kwargs={'variable_column': 'content', 'context_object': 'search'}, name='search'),
                       # Views for all objects of type
                       url(r'^members/$',
                           views.AllMembers.as_view(queryset=Member.objects.filter(is_current=True)),
                           name='all-members'),
                       url(r'^parties/$', views.AllParties.as_view(
                           queryset=Party.objects.filter(knesset__number=settings.CURRENT_KNESSET_NUMBER)),
                           name='all-parties'),
                       url(r'^tags/$', views.AllTags.as_view(queryset=Tag.objects.all()),
                           name='all-tags'),
                       # urls and views used only indirectly
                       url(r'^status_permalink/(?P<slug>[-_\w]+)/$', views.FacebookStatusDetailView.as_view(), name='status-detail'),
                       url(r'^fblogin/$', views.login_page, name='fblogin'),
                       url(r'^fblogin/get-data/$', views.get_data_from_facebook, name='get-data-from-facebook'),
                       url(r'^status_update/(?P<status_id>\w+)/$', views.status_update),
                       url(r'^add_tag_to_status/$', views.add_tag_to_status),
                       url(r'^add-tag/(?P<id>\d+)/$', views.add_tag,
                           name='add-tag'),
                       # unused Views for statuses
                       url(r'^comments/', views.OnlyCommentsView.as_view(), name='comments'),
                       url(r'^untagged/$', views.AllStatusesView.as_view(
                           queryset=Facebook_Status.objects.filter(tags=None, feed__persona__object_id__isnull=False).order_by('-published')),
                           kwargs={'context_object': 'untagged'},
                           name='untagged'),
)

urlpatterns = format_suffix_patterns(urlpatterns)

