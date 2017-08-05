from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils import timezone
from django.conf import settings
from django.contrib.contenttypes.models import ContentType

from facebook_feeds.models import Facebook_Feed, Facebook_Persona, \
    Facebook_Status, Feed_Popularity

from mks.models import Knesset, Member, Party


class CoreViewsTests(TestCase):
    def setUp(self):
        knesset = Knesset(number=settings.CURRENT_KNESSET_NUMBER)
        knesset.save()
        party = Party(knesset=knesset,
                      name="test_party")
        party.save()
        member = Member(current_party=party, name="test_member")
        member.save()
        member_content_type = ContentType.objects.get(app_label="mks",
                                                      model="member")
        persona = Facebook_Persona(object_id=member.id,
                                   content_type=member_content_type)

        persona.save()
        facebook_feed = Facebook_Feed(vendor_id=123,
                                      name="test_feed",
                                      is_current=True,
                                      feed_type='PP',
                                      persona=persona)
        facebook_feed.save()
        persona.main_feed = facebook_feed.id
        persona.save()

        for status_id in xrange(10):
            creation_date = timezone.now() - timezone.timedelta(days=status_id)
            facebook_status = Facebook_Status(feed=facebook_feed,
                                              status_id=str(status_id),
                                              content="foo",
                                              published=creation_date,
                                              updated=timezone.now())
            facebook_status.save()
        for day in xrange(10):
            creation_date = timezone.now() - timezone.timedelta(days=day)
            popularity = Feed_Popularity(feed=facebook_feed,
                                         date_of_creation=creation_date,
                                         fan_count=day * 100)
            popularity.save()

    def tearDown(self):
        Knesset.objects.all().delete()
        Party.objects.all().delete()
        Member.objects.all().delete()
        Facebook_Feed.objects.all().delete()
        Facebook_Status.objects.all().delete()
        Facebook_Persona.objects.all().delete()

    def test_about_us_view(self):
        url = reverse("about")
        print Knesset.objects.all().count()
        response = self.client.get(url)
        self.assertTrue(response.status_code == 200)
