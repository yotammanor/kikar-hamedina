from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns
from . import plain_views
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag

urlpatterns = patterns('',

    url(r'^$', plain_views.HomeView.as_view(), name='plain-index'),
    url(r'^untagged/$', plain_views.HomeView.as_view(
        queryset=Facebook_Status.objects.filter(tags=None).order_by('published')
    ), name='plain-untagged'),
    url(r'^add-tag/(?P<id>\d+)/$', plain_views.add_tag, name='add-tag'),
    # url(r'^party/$', views.party, name='plain-party'),
    # url(r'^person/$', views.person, name='plain-person'),

)

urlpatterns = format_suffix_patterns(urlpatterns)

