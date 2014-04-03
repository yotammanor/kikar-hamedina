from persons.models import Person, Party
from core.models import Tag, Facebook_Status, Facebook_Feed, Feed_Popularity
from django.db.models import F, Count
from kikar_hamedina.settings.base import FACEBOOK_APP_ID

NUMBER_OF_TOP_POLITICIANS_TO_BRING = 12
NUMBER_OF_TOP_TAGS_TO_BRING = 12


def generic(request):

    persons = Person.objects.all()
    persons_with_feed = [person for person in persons if person.feeds.select_related()]
    list_of_persons = list()
    for person in persons_with_feed:
        try:
            feed_popularity = person.feeds.select_related().first().current_fan_count
            list_of_persons.append({'person': person, 'popularity': feed_popularity})
        except:
            pass
    sorted_list_of_persons = sorted(list_of_persons, key=lambda x: x['popularity'], reverse=True)

    return {
        'navPersons': [x['person'] for x in sorted_list_of_persons][:NUMBER_OF_TOP_POLITICIANS_TO_BRING],
        'navParties': Party.objects.all().order_by('name'),
        'navTags': Tag.objects.filter(is_for_main_display=True)
                       .annotate(num_of_posts=Count('statuses'))
                       .order_by('-num_of_posts')[:NUMBER_OF_TOP_TAGS_TO_BRING],
        'facebook_app_id': FACEBOOK_APP_ID,
    }
