from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import plain_views
from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag
from mks.models import Party, Member
from kikar_hamedina.settings.base import CURRENT_KNESSET_NUMBER


urlpatterns = patterns('',
                       url(r'^$', plain_views.HomepageView.as_view(), name='plain-index'),
                       url(r'^all-statuses/$',
                           plain_views.AllStatusesView.as_view(queryset=Facebook_Status.objects.order_by('-published')),
                           kwargs={'context_object': 'index'},
                           name='plain-all-statuses'),
                       url(r'^untagged/$', plain_views.AllStatusesView.as_view(
                           queryset=Facebook_Status.objects.filter(tags=None).order_by('-published')),
                           kwargs={'context_object': 'untagged'},
                           name='plain-untagged'),
                       url(r'^add-tag/(?P<id>\d+)/$', plain_views.add_tag,
                           name='add-tag'),
                       url(r'^party/(?P<id>\d+)/$', plain_views.PartyView.as_view(),
                           kwargs={'variable_column': 'feed__person__party__id',  # TODO: refactor!
                                   'context_object': 'party'},
                           name='plain-party'),
                       url(r'^member/(?P<id>\d+)/$', plain_views.MemberView.as_view(),
                           kwargs={'variable_column': 'feed__object_id',
                                   'context_object': 'member'},
                           name='plain-member'),
                       url(r'^tag/(?P<search_field>\w+)/(?P<id>[\w\s\-:"\'!\?&\.#]+)/$', plain_views.TagView.as_view(),
                           kwargs={'variable_column': 'tags',
                                   'context_object': 'tag'},
                           name='plain-tag'),
                       url(r'^search/$', plain_views.SearchView.as_view(),
                           kwargs={'variable_column': 'content', 'context_object': 'search'}, name='plain-search'),
                       url(r'^searchgui/$', plain_views.SearchGuiView.as_view(), name="search-gui"),
                       url(r'^members/$',
                           plain_views.AllMembers.as_view(queryset=Member.objects.filter(is_current=True)),
                           name='all-members'),
                       url(r'^parties/$', plain_views.AllParties.as_view(
                           queryset=Party.objects.filter(knesset__number=CURRENT_KNESSET_NUMBER)),
                           name='all-parties'),
                       url(r'^tags/$', plain_views.AllTags.as_view(queryset=Tag.objects.all()),
                           name='all-tags'),
                       url(r'^about/$', plain_views.about_page, name='about', ),
                       url(r'^fblogin/$', plain_views.login_page, name='fblogin'),
                       url(r'^fblogin/get-data/$', plain_views.get_data_from_facebook, name='get-data-from-facebook'),
                       url(r'^status_update/(?P<status_id>\w+)/$', plain_views.status_update),
                       url(r'^search_bar/$', plain_views.search_bar),

)

urlpatterns = format_suffix_patterns(urlpatterns)

