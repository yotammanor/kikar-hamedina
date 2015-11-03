from operator import or_, and_
import re

from collections import defaultdict
from django.db.models import Q

from facebook_feeds.models import Facebook_Feed
from kikartags.models import Tag
from core.models import MEMBER_MODEL, PARTY_MODEL, IS_ELECTIONS_MODE
from core.params import RE_SPLIT_WORD_UNICODE, PG_RE_PHRASE_START, PG_RE_PHRASE_END, PG_RE_NON_WORD_CHARS, \
    DEFAULT_OPERATOR


class NoDefaultProvided(object):
    pass


def getattrd(obj, name, default=NoDefaultProvided):
    """
    Same as getattr(), but allows dot notation lookup
    Discussed in:
    http://stackoverflow.com/questions/11975781
    """
    try:
        return reduce(getattr, name.split("."), obj)
    except AttributeError, e:
        if default != NoDefaultProvided:
            return default
        raise


def join_queries(q1, q2, operator):
    """Join two queries with operator (e.g. or_, and_) while handling empty queries"""
    return operator(q1, q2) if (q1 and q2) else (q1 or q2)


def get_parsed_request(get_params):
    print 'request:', get_params

    # adds all member ids explicitly searched for.
    members_ids = []
    if 'members' in get_params.keys():
        members_ids = [int(member_id) for member_id in get_params['members'].split(',')]

    # adds to member_ids all members belonging to parties explicitly searched for.
    parties_ids = []
    if 'parties' in get_params.keys():
        parties_ids = [int(party_id) for party_id in get_params['parties'].split(',')]
        parties = PARTY_MODEL.objects.filter(id__in=parties_ids)
        for party in parties:
            for member in party.current_members():
                if member.id not in members_ids:
                    members_ids.append(member.id)

    # tags searched for.
    tags_ids = []
    if 'tags' in get_params.keys():
        tags_ids = [int(tag_id) for tag_id in get_params['tags'].split(',')]

    # keywords searched for, comma separated
    phrases = []
    if 'search_str' in get_params.keys():
        search_str_stripped = get_params['search_str'].strip()[1:-1]  # removes quotes from beginning and end.
        phrases = [phrase for phrase in search_str_stripped.split('","')]

    print 'parsed request:', members_ids, parties_ids, tags_ids, phrases
    return {'members_ids': members_ids, 'parties_ids': parties_ids, 'tags_ids': tags_ids, 'phrases': phrases}


def parse_to_q_object(get_params, params_dict):
    member_query = MEMBER_MODEL.objects.filter(id__in=params_dict['members_ids'])
    fixed_member_ids = [member.id for member in member_query]
    if IS_ELECTIONS_MODE:
        feeds = Facebook_Feed.objects.filter(persona__alt_object_id__in=fixed_member_ids)
    else:
        feeds = Facebook_Feed.objects.filter(persona__object_id__in=fixed_member_ids)

    # all members asked for (through member search of party search), with OR between them.
    members_OR_parties_Q = Q()
    if feeds:
        members_OR_parties_Q = Q(feed__in=feeds)

    # tags - search for all tags specified by their id
    tags_Q = Q()
    if params_dict['tags_ids']:
        # | Q(tags__synonyms__proper_form_of_tag__id=tag_id)
        tag_bundle_ids = [tag.id for tag in Tag.objects.filter_bundle(id__in=params_dict['tags_ids'])]
        tags_to_queries = [Q(tags__id=tag_id) for tag_id in tag_bundle_ids]
        print 'tags_to_queries:', len(tags_to_queries)
        for query_for_single_tag in tags_to_queries:
            # tags_Q is empty for the first iteration
            tags_Q = join_queries(query_for_single_tag, tags_Q, or_)

    print 'tags_Q:', tags_Q

    # keywords - searched both in content and in tags of posts.
    search_str_Q = Q()
    # If regexes cause security / performance problem - switch this flag
    # to False to use a (not as good) text search instead
    use_regex = True
    for phrase in params_dict['phrases']:
        if use_regex:
            # Split into words (remove whitespace, punctuation etc.)
            words = re.split(RE_SPLIT_WORD_UNICODE, phrase)
            # If there are no words - ignore this phrase
            if words:
                # Build regex - all words we've found separated by 'non-word' characters
                # and also allow VAV and/or HEI in front of each word.
                # NOTE: regex syntax is DB dependent - this works on postgres
                re_words = [u'\u05D5?\u05D4?' + word for word in words]
                regex = PG_RE_PHRASE_START + PG_RE_NON_WORD_CHARS.join(re_words) + PG_RE_PHRASE_END
                search_str_Q = join_queries(Q(content__iregex=regex), search_str_Q, or_)
        else:
            # Fallback code to use if we want to disable regex-based search
            search_str_Q = join_queries(Q(content__icontains=phrase), search_str_Q, or_)
        search_str_Q = Q(tags__name__contains=phrase) | search_str_Q

    # tags query and keyword query concatenated. Logic is set according to request input
    request_operator = get_params.get('tags_and_search_str_operator', DEFAULT_OPERATOR)

    print 'selected_operator:', request_operator
    selected_operator = and_ if request_operator == 'and_operator' else or_

    search_str_with_tags_Q = join_queries(tags_Q, search_str_Q, selected_operator)

    print 'search_str_with_tags_Q:', search_str_with_tags_Q
    print '\n'

    query_Q = join_queries(members_OR_parties_Q, search_str_with_tags_Q, and_)

    print 'query to be executed:', query_Q
    return query_Q
