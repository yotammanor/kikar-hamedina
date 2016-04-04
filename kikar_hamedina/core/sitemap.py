from django.contrib.sitemaps import Sitemap
from mks.models import Member, Party
from core.models import MEMBER_MODEL, PARTY_MODEL
from django.conf import settings
from django.utils import timezone

DEFAULT_MIN_DATE = timezone.make_aware(timezone.datetime(1970, 1, 1, 0, 0, 0, 0))

import pytz


class MkSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return MEMBER_MODEL.objects.filter(is_current=True)

    def lastmod(self, obj):
        if obj.facebook_persona and obj.facebook_persona.get_main_feed.facebook_status_set.exists():
            return obj.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first().published
        return DEFAULT_MIN_DATE


class PartySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.5

    def items(self):
        return PARTY_MODEL.current_knesset.all()

    def lastmod(self, obj):
        members = obj.current_members()
        update_dates = [
            member.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first().published for
            member in members if
            member.facebook_persona and member.facebook_persona.get_main_feed.facebook_status_set.exists()]
        return max(update_dates + [DEFAULT_MIN_DATE])


class AbstractSitemapClass():
    url = None

    def get_absolute_url(self):
        return self.url


class StaticViewSitemap(Sitemap):
    priority = 1
    changefreq = "daily"

    pages = {
        'home': '/',
        'billboards': '/billboards',
        'about': '/about',
    }
    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]
        main_sitemaps.append(sitemap_class)

    def items(self):
        return self.main_sitemaps
