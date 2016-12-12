from operator import or_, and_
import re
import dateutil
from collections import defaultdict
from django.db.models import Q
from django.utils import timezone
from django.utils.datastructures import MultiValueDictKeyError
from django.conf import settings
from facebook_feeds.models import Facebook_Feed
from kikartags.models import Tag
from core.models import MEMBER_MODEL, PARTY_MODEL, IS_ELECTIONS_MODE
from core.params import RE_SPLIT_WORD_UNICODE, PG_RE_PHRASE_START, \
    PG_RE_PHRASE_END, PG_RE_NON_WORD_CHARS, \
    DEFAULT_OPERATOR, FILTER_BY_DATE_DEFAULT_START_DATE, \
    ALLOWED_FIELDS_FOR_ORDER_BY, DEFAULT_STATUS_ORDER_BY


def get_order_by(request):
    """
    This function receives a request, and parses order_by parameter, if exists into
    an array of approved and validated order_by fields.
    If fails, falls back to a default order-by (-published)
    """
    try:
        order_by_str = request.GET['order_by']
        order_by = [x for x in order_by_str.split(',') if
                    x.replace("-", "").split("__")[
                        0] in ALLOWED_FIELDS_FOR_ORDER_BY]  # tests for feed__*
    except MultiValueDictKeyError:
        order_by = [DEFAULT_STATUS_ORDER_BY]
    if not order_by:
        order_by = [DEFAULT_STATUS_ORDER_BY]
    return order_by


def get_date_range_dict():
    filter_by_date_default_end_date = timezone.now()

    date_range_dict = {
        'default': {'start_date': FILTER_BY_DATE_DEFAULT_START_DATE,
                    'end_date': filter_by_date_default_end_date},

        'day': {'start_date': timezone.now() - timezone.timedelta(days=1),
                'end_date': filter_by_date_default_end_date},

        'current_day': {
            'start_date': timezone.datetime(timezone.now().year,
                                            timezone.now().month,
                                            timezone.now().day,
                                            tzinfo=timezone.utc),
            'end_date': filter_by_date_default_end_date},

        'week': {'start_date': timezone.now() - timezone.timedelta(days=7),
                 'end_date': filter_by_date_default_end_date},

        'two_weeks': {
            'start_date': timezone.now() - timezone.timedelta(days=14),
            'end_date': filter_by_date_default_end_date},

        'month': {'start_date': timezone.now() - timezone.timedelta(days=31),
                  'end_date': filter_by_date_default_end_date},

        'current_month': {
            'start_date': timezone.datetime(timezone.now().year,
                                            timezone.now().month, 1,
                                            tzinfo=timezone.utc),
            'end_date': filter_by_date_default_end_date
        },
        'current_year': {
            'start_date': timezone.datetime(timezone.now().year, 1, 1,
                                            tzinfo=timezone.utc),
            'end_date': filter_by_date_default_end_date
        },
        'elections_20': {
            # Dates are set based on information from Wikipedia:
            # he.wikipedia.org/wiki/%D7%94%D7%91%D7%97%D7%99%D7%A8%D7%95%D7%AA_%D7%9C%D7%9B%D7%A0%D7%A1%D7%AA_%D7%94%D7%A2%D7%A9%D7%A8%D7%99%D7%9D
            'start_date': timezone.datetime(2014, 12, 8, tzinfo=timezone.utc),
            'end_date': timezone.datetime(2015, 3, 17, tzinfo=timezone.utc)
        },
        'protective-edge': {
            # Dates are set based on information from Wikipedia:
            # he.wikipedia.org/wiki/%D7%9E%D7%91%D7%A6%D7%A2_%D7%A6%D7%95%D7%A7_%D7%90%D7%99%D7%AA%D7%9F
            'start_date': timezone.datetime(2014, 7, 8, tzinfo=timezone.utc),
            'end_date': timezone.datetime(2014, 8, 26, tzinfo=timezone.utc)
        },
    }
    return date_range_dict


def filter_by_date(request, datetime_field='published'):
    date_range_dict = get_date_range_dict()
    date_time_field_range = datetime_field + '__range'
    if 'from_date' in request.GET or 'to_date' in request.GET:
        if 'from_date' in request.GET:
            start_date = dateutil.parser.parse(request.GET['from_date'])
        else:
            start_date = date_range_dict['default']['start_date']
        if 'to_date' in request.GET:
            end_date = dateutil.parser.parse(request.GET['to_date'])
        else:
            end_date = date_range_dict['default']['end_date']
        range_value = (start_date, end_date)
        return Q(**{date_time_field_range: range_value})

    elif 'range' in request.GET:
        filter_range_arg = request.GET['range']
    else:
        filter_range_arg = 'default'

    try:
        start_date = date_range_dict[filter_range_arg]['start_date']
        end_date = date_range_dict[filter_range_arg]['end_date']
    except KeyError:
        start_date = date_range_dict['default']['start_date']
        end_date = date_range_dict['default']['end_date']

    range_value = (start_date, end_date)
    return Q(**{date_time_field_range: range_value})


def join_queries_discard_empty(q1, q2, operator):
    """Join two queries with operator (e.g. or_, and_) while handling empty queries"""
    return operator(q1, q2) if (q1 and q2) else (q1 or q2)


def get_parsed_request(get_params):
    if settings.DEBUG:
        print('request:', get_params)

    # adds all member ids explicitly searched for.
    members_ids = []
    if 'members' in get_params.keys():
        members_ids = [int(member_id) for member_id in
                       get_params['members'].split(',')]

    # adds to member_ids all members belonging to parties explicitly searched for.
    parties_ids = []
    if 'parties' in get_params.keys():
        parties_ids = [int(party_id) for party_id in
                       get_params['parties'].split(',')]
        parties = PARTY_MODEL.objects.filter(id__in=parties_ids)
        for party in parties:
            for member in party.current_members():
                if member.id not in members_ids:
                    members_ids.append(member.id)

    # tags searched for.
    tags_ids = []
    if 'tags' in get_params.keys():
        tags_ids = [int(tag_id) for tag_id in get_params['tags'].split(',')]

    phrases = parse_search_phrases(get_params)

    excluded = []
    if 'excluded' in get_params.keys():
        excluded = [id for id in get_params['excluded'].split(',')]

    if settings.DEBUG:
        print('parsed request:', members_ids, parties_ids, tags_ids, phrases)
    return {'members_ids': members_ids,
            'parties_ids': parties_ids,
            'tags_ids': tags_ids,
            'phrases': phrases,
            'excluded': excluded}


def parse_search_phrases(get_params):
    phrases = []
    if 'search_str' in get_params.keys():
        phrases_raw = [phrase for phrase
                       in get_params['search_str'].split(',')]
        for phrase in phrases_raw:
            phrase = phrase.strip()
            phrase = remove_optional_quotes_from_phrase(phrase)
            phrase = phrase.strip()
            phrases.append(phrase)
    return phrases


def remove_optional_quotes_from_phrase(phrase, quote_symbol='"'):
    if phrase.startswith(quote_symbol) and phrase.endswith(quote_symbol):
        phrase = phrase.strip(quote_symbol)
    return phrase


def parse_to_q_object(get_params, params_dict):
    member_query = MEMBER_MODEL.objects.filter(
        id__in=params_dict['members_ids'])
    fixed_member_ids = [member.id for member in member_query]
    if IS_ELECTIONS_MODE:
        feeds = Facebook_Feed.objects.filter(
            persona__alt_object_id__in=fixed_member_ids)
    else:
        feeds = Facebook_Feed.objects.filter(
            persona__object_id__in=fixed_member_ids)

    # all members asked for (through member search of party search), with OR between them.
    members_OR_parties_Q = Q()
    if feeds:
        members_OR_parties_Q = Q(feed__id__in=[x.id for x in feeds])

    selected_operator = get_phrases_operator(get_params)
    search_str_with_tags_Q = build_phrases_and_tags_query(params_dict,
                                                          selected_operator)
    query_Q = join_queries_discard_empty(members_OR_parties_Q,
                                         search_str_with_tags_Q, and_)

    if params_dict['excluded']:
        excluded_query = Q(status_id__in=params_dict['excluded'])
        excluded_query.negate()
        query_Q = join_queries_discard_empty(query_Q, excluded_query, and_)

    if settings.DEBUG:
        from qserializer import QSerializer
        qser = QSerializer()
        print('query to be executed:')
        from pprint import pprint
        pprint(qser.serialize(query_Q.clone()))
    return query_Q


def build_phrases_and_tags_query(params_dict, selected_operator):
    tags_Q = build_tags_query(params_dict, selected_operator)
    search_str_Q = build_phrases_query(params_dict, selected_operator)

    search_str_with_tags_Q = join_queries_discard_empty(tags_Q, search_str_Q,
                                                        selected_operator)
    if settings.DEBUG:
        print ('search_str_with_tags_Q:', search_str_with_tags_Q)
        print ('\n')
    return search_str_with_tags_Q


def build_phrases_query(params_dict, selected_operator):
    '''keywords - searched both in content and in tags of posts.'''
    search_str_Q = Q()
    # If regexes cause security / performance problem - switch this flag
    # to False to use a (not as good) text search instead
    use_regex = True
    for phrase in params_dict['phrases']:
        if use_regex:
            new_phrase_Q = build_query_phrase_as_regex(phrase)
        else:
            # Fallback code to use if we want to disable regex-based search
            new_phrase_Q = Q(content__icontains=phrase)
            new_phrase_Q = join_queries_discard_empty(
                Q(tags__name__contains=phrase), new_phrase_Q, or_)

        search_str_Q = join_queries_discard_empty(new_phrase_Q, search_str_Q,
                                                  selected_operator)
    return search_str_Q


def build_tags_query(params_dict, selected_operator):
    '''tags - search for all tags specified by their id.
    '''
    tags_Q = Q()
    if params_dict['tags_ids']:
        # | Q(tags__synonyms__proper_form_of_tag__id=tag_id)
        tag_bundle_ids = [tag.id for tag in Tag.objects.filter_bundle(
            id__in=params_dict['tags_ids'])]
        tags_to_queries = [Q(tags__id=tag_id) for tag_id in tag_bundle_ids]
        if settings.DEBUG:
            print('tags_to_queries:', len(tags_to_queries))
        for query_for_single_tag in tags_to_queries:
            # tags_Q is empty for the first iteration
            tags_Q = join_queries_discard_empty(query_for_single_tag, tags_Q,
                                                selected_operator)
    if settings.DEBUG:
        print('tags_Q:', tags_Q)

    return tags_Q


def build_query_phrase_as_regex(phrase):
    # Split into sub_phrases (remove whitespace, punctuation etc.)
    sub_phrases = re.split(RE_SPLIT_WORD_UNICODE, phrase)
    # If there are no sub_phrases - ignore this phrase
    search_str_Q = Q()
    if sub_phrases:
        # Build regex - all sub_phrases we've found separated by 'non-word' characters
        # and also allow VAV and/or HEI in front of each word.
        # NOTE: regex syntax is DB dependent - this works on postgres
        re_words = [u'\u05D5?\u05D4?' + word for word in sub_phrases]
        regex = PG_RE_PHRASE_START + PG_RE_NON_WORD_CHARS.join(
            re_words) + PG_RE_PHRASE_END
        search_str_Q = Q(content__iregex=regex)
    return search_str_Q


def get_phrases_operator(get_params):
    # tags query and keyword query concatenated. Logic is set according to request input
    request_operator = get_params.get('operator', DEFAULT_OPERATOR)
    if settings.DEBUG:
        print('selected_operator:', request_operator)
    selected_operator = and_ if request_operator == 'and' else or_
    return selected_operator


def apply_request_params(query, request):
    """Apply request params to DB query. This currently includes 'range'
    and 'order_by'
    :param request: """
    date_range_Q = filter_by_date(request)
    order_by = get_order_by(request)
    return query.filter(date_range_Q).order_by(*order_by)
