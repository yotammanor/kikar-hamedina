from core.models import PARTY_MODEL, MEMBER_MODEL
from facebook_feeds.models import Tag as OldTag, Facebook_Status, Facebook_Feed, Feed_Popularity
from kikartags.models import Tag as Tag
from django.db.models import Count
from kikar_hamedina.settings import FACEBOOK_APP_ID, CURRENT_KNESSET_NUMBER, CURRENT_ELECTED_KNESSET_NUMBER, \
    IS_ELECTIONS_MODE
from django.core.cache import cache
import datetime


NUMBER_OF_TOP_PARTIES_TO_BRING = 12
NUMBER_OF_TOP_POLITICIANS_TO_BRING = 12
NUMBER_OF_TOP_TAGS_TO_BRING = 12
TAGS_FROM_LAST_DAYS = 7

if IS_ELECTIONS_MODE:
    KNESSET_NUMBER = CURRENT_ELECTED_KNESSET_NUMBER
else:
    KNESSET_NUMBER = CURRENT_KNESSET_NUMBER


def generic(request):
    result = cache.get("generic_context")
    if result is None:
        result = get_context(request)
        cache.set("generic_context", result, 600)

    # Tags info isn't cached as it needs to be updated dynamically
    relevant_statuses = Facebook_Status.objects.filter(published__gte=(
        datetime.date.today() - datetime.timedelta(days=TAGS_FROM_LAST_DAYS)))

    result['navTags'] = (Tag.objects.filter(is_for_main_display=True,
                                            kikartags_taggeditem_items__object_id__in=[status.id for status in
                                                                                       relevant_statuses])
                         .annotate(number_of_posts=Count('kikartags_taggeditem_items'))
                         .order_by('-number_of_posts')[:NUMBER_OF_TOP_TAGS_TO_BRING])

    return result


def get_context(request):
    # members = MEMBER_MODEL.objects.filter(is_current=True)
    members = MEMBER_MODEL.objects.all()
    members_with_persona = [member for member in members if member.facebook_persona]
    members_with_feed = [member for member in members_with_persona if member.facebook_persona.feeds.all()]
    list_of_members = list()
    for member in members_with_feed:
        try:
            feed_popularity = member.facebook_persona.get_main_feed.current_fan_count
            list_of_members.append({'member': member, 'popularity': feed_popularity, 'name': member.name})
        except:
            pass
    sorted_list_of_members_by_name = sorted(list_of_members, key=lambda l: l['name'], reverse=False)
    sorted_list_of_members_by_popularity = sorted(list_of_members, key=lambda l: l['popularity'], reverse=True)

    if IS_ELECTIONS_MODE:
        nav_parties = PARTY_MODEL.objects.filter(knesset__number=KNESSET_NUMBER).annotate(
            num_of_members=Count('candidates')).order_by('-num_of_members')
    else:
        nav_parties = PARTY_MODEL.objects.filter(knesset__number=KNESSET_NUMBER).order_by('-number_of_members')

    return {
        'navMembers': [x['member'] for x in sorted_list_of_members_by_name],
        'navMembersTop': [x['member'] for x in sorted_list_of_members_by_popularity],
        'navParties': nav_parties,
        'facebook_app_id': FACEBOOK_APP_ID,
    }
