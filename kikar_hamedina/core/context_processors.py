from core.models import Person, Party, Tag, Facebook_Status, Facebook_Feed, Feed_Popularity
from django.db.models import F, Count
from kikar_hamedina.settings.base import FACEBOOK_APP_ID

NUMBER_OF_TOP_POLITICIANS_TO_BRING = 12
NUMBER_OF_TOP_TAGS_TO_BRING = 12


def generic(request):
    persons = Person.objects.filter(facebook_feed__gt=0)
    list_of_persons = list()
    for person in persons:
        try:
            feed_popularity = person.facebook_feed_set.first().current_fan_count
            print feed_popularity
            list_of_persons.append({'person': person, 'popularity': feed_popularity})
        except:
            pass
    sorted_list_of_persons = sorted(list_of_persons, key=lambda x: x['popularity'], reverse=True)
    print sorted_list_of_persons

    return {
        'navPersons': [x['person'] for x in sorted_list_of_persons][:NUMBER_OF_TOP_POLITICIANS_TO_BRING],
        'navParties': Party.objects.all().order_by('name'),
        'navTags': Tag.objects.filter(is_for_main_display=True)
                       .annotate(num_of_posts=Count('statuses'))
                       .order_by('-num_of_posts')[:NUMBER_OF_TOP_TAGS_TO_BRING],
        'facebook_app_id': FACEBOOK_APP_ID,
    }
