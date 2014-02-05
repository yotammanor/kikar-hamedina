from core.models import Person, Party, Tag, Facebook_Status, Facebook_Feed
from django.db.models import F, Count
from kikar_hamedina.settings.base import FACEBOOK_APP_ID

NUMBER_OF_TOP_POLITICIANS_TO_BRING = 10
NUMBER_OF_TOP_TAGS_TO_BRING = 10


def generic(request):
    return {
        'navPersons': Person.objects.filter(facebook_feed__gt=0)
                      .order_by('-facebook_feed__fan_count')[:NUMBER_OF_TOP_POLITICIANS_TO_BRING],
        'navParties': Party.objects.all().order_by('name'),
        'navTags': Tag.objects.all()
                   .annotate(num_of_posts=Count('statuses'))
                   .order_by('-num_of_posts')[:NUMBER_OF_TOP_TAGS_TO_BRING],
        'facebook_app_id': FACEBOOK_APP_ID,
        }
