from django.contrib.sitemaps import Sitemap
from mks.models import Member, Party
from django.conf import settings
from datetime import datetime
import pytz

class MkSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Member.objects.filter(is_current=True);


    def lastmod(self, obj):
        if (obj.facebook_persona != None and
            # I have no idea why but the set is sometime empty
            obj.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first() != None):

            # TODO: I think I am not getting the correct date here, for example 867 supposed to have a different date (on my data of course)
            #if (obj.id == 867):
             #   print 'bla'
              #  print 'for id 867 date is: ' + str(obj.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first().locally_updated);

            return obj.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first().locally_updated;
        else:
            return datetime(1970,1,1,10,0,0,0, pytz.UTC);


class PartySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return Party.objects.filter(knesset__number=settings.CURRENT_KNESSET_NUMBER);

    def lastmod(self,obj):
        maxDate = datetime(1970,1,1,10,0,0,0, pytz.UTC);
        for m in Member.objects.filter(current_party=obj.id).all():
            if (m.facebook_persona != None and
             # I have no idea why but the set is sometime empty
             m.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first() != None):
                curLastUpdate = m.facebook_persona.get_main_feed.facebook_status_set.order_by('-published').first().locally_updated;
                if maxDate < curLastUpdate:
                    maxDate = curLastUpdate;

        return maxDate;

class AbstractSitemapClass():

    url = None
    def get_absolute_url(self):
        return self.url

class StaticViewSitemap(Sitemap):
    priority = 1
    changefreq = "daily"

    pages = {
             'home':'/',
             'billboards':'/billboards',
             'about' : '/about',
             }
    main_sitemaps = []
    for page in pages.keys():
        sitemap_class = AbstractSitemapClass()
        sitemap_class.url = pages[page]
        main_sitemaps.append(sitemap_class)

    def items(self):
        return self.main_sitemaps
