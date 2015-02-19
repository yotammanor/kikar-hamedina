# encoding: utf-8

from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from facebook_feeds.models import Facebook_Status
from core.models import PARTY_MODEL, MEMBER_MODEL
from django.utils import timezone
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from reporting.models import RSSFeedKeyWord
from django.contrib.auth.models import User
from core.views import SearchView
from django.http.request import HttpRequest


class LatestStatusesRSSFeed(Feed):
    title = "Police beat site news"
    link = "/?range=week"
    description = "Updates on changes and additions to police beat central."

    def items(self):
        return Facebook_Status.objects.filter(published__gte=timezone.now() - timezone.timedelta(days=1)).order_by(
            '-published')

    def item_title(self, item):
        return "Status by %s" % item.feed.persona.owner.name

    def item_description(self, item):
        return item.content

    def item_link(self, item):
        return reverse('status-detail', args=[item.status_id])


class PartyRSSFeed(Feed):
    description_template = 'rss/party_description.html'

    def get_object(self, request, party_id):
        return get_object_or_404(PARTY_MODEL, pk=party_id)

    def title(self, obj):
        return "Kikar: facebook_statuses for %s" % obj.name

    def link(self, obj):
        return reverse('party', args=[obj.id])

    def description(self, obj):
        return "Kikar: facebook_statuses for %s" % obj.name

    def item_link(self, item):
        return reverse('status-detail', args=[item.status_id])

    def items(self, obj):
        return Facebook_Status.objects.filter(
            feed__persona__alt_object_id__in=[x.id for x in MEMBER_MODEL.objects.filter(candidates_list=obj)]).order_by(
            '-published')[:30]


class KeywordsByUserRSSFeed(Feed):
    description_template = 'rss/party_description.html'

    def get_object(self, request, user_id):
        return get_object_or_404(User, pk=user_id)

    def title(self, obj):
        return "Kikar: facebook_statuses with keywords set by %s" % obj

    def link(self, obj):
        return '%s/?search_str=%s' % (reverse('search'), ','.join([x.keyword for x in obj.words_in_rss_feed.all()]))

    def description(self, obj):
        return "Kikar: facebook_statuses with keywords set by %s" % obj

    def item_link(self, item):
        return reverse('status-detail', args=[item.status_id])

    def items(self, obj):
        search_view = SearchView(request=HttpRequest())

        Query_Q = search_view.parse_q_object(members_ids=[], parties_ids=[], tags_ids=[],
                                             phrases=[x.keyword for x in obj.words_in_rss_feed.all()])
        return Facebook_Status.objects.filter(Query_Q).order_by('-published')[:30]

