# -*- coding: utf-8 -*-
import datetime
import json
import re
from operator import or_, and_
from unidecode import unidecode

from django.core.urlresolvers import reverse
from django.conf import settings
from django.utils.datastructures import MultiValueDictKeyError
from django.utils import timezone
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.decorators.csrf import csrf_protect
from django.template import RequestContext
from django.db.models import Count, Q

import facebook
from facebook import GraphAPIError
from endless_pagination.views import AjaxListView

from facebook_feeds.management.commands import updatestatus
from facebook_feeds.models import Facebook_Status, Facebook_Feed, User_Token, Feed_Popularity, TAG_NAME_REGEX, \
    Facebook_Persona
from facebook_feeds.models import Tag as OldTag
from kikartags.models import Tag as Tag, HasSynonymError, TaggedItem
from core.insights import StatsEngine
from core.billboards import Billboards
from core.models import MEMBER_MODEL, PARTY_MODEL
# current knesset number
MAX_UNTAGGED_POSTS = 1000
CURRENT_KNESSET_NUMBER = getattr(settings, 'CURRENT_KNESSET_NUMBER', 19)

# Elections mode (use candidates instead of MKs)
IS_ELECTIONS_MODE = getattr(settings, 'IS_ELECTIONS_MODE', False)

# used for calculating top gainer of fan_count
MIN_FAN_COUNT_FOR_REL_COMPARISON = getattr(settings, 'MIN_FAN_COUNT_FOR_REL_COMPARISON', 5000)
DEFAULT_POPULARITY_DIF_COMPARISON_TYPE = getattr(settings, 'DEFAULT_POPULARITY_DIF_COMPARISON_TYPE', 'rel')
POPULARITY_DIF_DAYS_BACK = getattr(settings, 'POPULARITY_DIF_DAYS_BACK', 30)

# search logic default operator
DEFAULT_OPERATOR = getattr(settings, 'DEFAULT_OPERATOR', 'or_operator')

# order by default
DEFAULT_STATUS_ORDER_BY = getattr(settings, 'DEFAULT_STATUS_ORDER_BY', '-published')
allowed_fields_for_order_by = [field.name for field in Facebook_Status._meta.fields]
ALLOWED_FIELDS_FOR_ORDER_BY = getattr(settings, 'ALLOWED_FIELDS_FOR_ORDER_BY', allowed_fields_for_order_by)

# filter by date options
FILTER_BY_DATE_DEFAULT_START_DATE = getattr(settings, 'FILTER_BY_DATE_DEFAULT_START_DATE',
                                            timezone.datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc))

# hot-topics page
NUMBER_OF_LAST_DAYS_FOR_HOT_TAGS = getattr(settings, 'NUMBER_OF_LAST_DAYS_FOR_HOT_TAGS', 7)

# needs_refresh - Constants for quick status refresh
MAX_STATUS_AGE_FOR_REFRESH = getattr(settings, 'MAX_STATUS_AGE_FOR_REFRESH', 60 * 60 * 24 * 2)  # 2 days
MIN_STATUS_REFRESH_INTERVAL = getattr(settings, 'MIN_STATUS_REFRESH_INTERVAL', 5)  # 5 seconds
MAX_STATUS_REFRESH_INTERVAL = getattr(settings, 'MAX_STATUS_REFRESH_INTERVAL', 60 * 10)  # 10 minutes

# Python regex for splitting words
RE_SPLIT_WORD_UNICODE = re.compile('\W+', re.UNICODE)

# Postgres regex for word boundaries. Unfortunately Hebrew support is not good, so can't use \W
# (\W detects Hebrew characters as non-word chars). Including built-in punctuation and whitespace
# plus a unicode range with some exotic spaces/dashes/quotes
PG_RE_NON_WORD_CHARS = u'[[:punct:][:space:]\u2000-\u201f]+'
# Start/end of phrase also allow beginning/end of statue
PG_RE_PHRASE_START = u'(^|%s)' % (PG_RE_NON_WORD_CHARS,)
PG_RE_PHRASE_END = u'(%s|$)' % (PG_RE_NON_WORD_CHARS,)


def get_date_range_dict():
    filter_by_date_default_end_date = timezone.now()

    date_range_dict = {'default': {'start_date': FILTER_BY_DATE_DEFAULT_START_DATE,
                                   'end_date': filter_by_date_default_end_date},

                       'week': {'start_date': timezone.now() - timezone.timedelta(days=7),
                                'end_date': filter_by_date_default_end_date},

                       'two_weeks': {'start_date': timezone.now() - timezone.timedelta(days=14),
                                     'end_date': filter_by_date_default_end_date},

                       'month': {'start_date': timezone.now() - timezone.timedelta(days=31),
                                 'end_date': filter_by_date_default_end_date},

                       'current_month': {
                           'start_date': timezone.datetime(timezone.now().year, timezone.now().month, 1,
                                                           tzinfo=timezone.utc),
                           'end_date': filter_by_date_default_end_date
                       },
                       'current_year': {
                           'start_date': timezone.datetime(timezone.now().year, 1, 1, tzinfo=timezone.utc),
                           'end_date': filter_by_date_default_end_date
                       },
                       'protective_edge': {
                           # Dates are set based on information from Wikipedia:
                           # he.wikipedia.org/wiki/%D7%9E%D7%91%D7%A6%D7%A2_%D7%A6%D7%95%D7%A7_%D7%90%D7%99%D7%AA%D7%9F
                           'start_date': timezone.datetime(2014, 7, 8, tzinfo=timezone.utc),
                           'end_date': timezone.datetime(2014, 8, 26, tzinfo=timezone.utc)
                       },
    }
    return date_range_dict


# TODO: refactor the next constant to use the pattern above
HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR = 3

NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY = 3

NUMBER_OF_TAGS_TO_PRESENT = 3

NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR = 3


def get_order_by(request):
    """
    This function receives a request, and parses order_by parameter, if exists into
    an array of approved and validated order_by fields.
    If fails, falls back to a default order-by (-published)
    """
    try:
        order_by_str = request.GET['order_by']
        order_by = [x for x in order_by_str.split(',') if
                    x.replace("-", "").split("__")[0] in ALLOWED_FIELDS_FOR_ORDER_BY]  # tests for feed__*
    except MultiValueDictKeyError:
        order_by = [DEFAULT_STATUS_ORDER_BY]
    if not order_by:
        order_by = [DEFAULT_STATUS_ORDER_BY]
    return order_by


def filter_by_date(request, datetime_field='published'):
    date_range_dict = get_date_range_dict()
    try:
        filter_range_arg = request.GET['range']
    except MultiValueDictKeyError:
        filter_range_arg = 'default'

    try:
        start_date = date_range_dict[filter_range_arg]['start_date']
        end_date = date_range_dict[filter_range_arg]['end_date']
    except KeyError:
        start_date = date_range_dict['default']['start_date']
        end_date = date_range_dict['default']['end_date']

    date_time_field_range = datetime_field + '__range'
    range_value = (start_date, end_date)
    return Q(**{date_time_field_range: range_value})


class StatusListView(AjaxListView):
    page_template = "core/facebook_status_list.html"

    def apply_request_params(self, query):
        """Apply request params to DB query. This currently includes 'range'
        and 'order_by' """
        date_range_Q = filter_by_date(self.request)
        order_by = get_order_by(self.request)
        return query.filter(date_range_Q).order_by(*order_by)


class AboutUsView(ListView):
    template_name = 'core/about_us.html'
    model = Facebook_Status

    def get_context_data(self, **kwargs):
        context = super(AboutUsView, self).get_context_data(**kwargs)
        new_statuses_last_day = Facebook_Status.objects.filter(published__gte=(
            datetime.date.today() - datetime.timedelta(days=1))).count()
        context['IS_ELECTION_MODE'] = IS_ELECTIONS_MODE
        context['statuses_last_day'] = new_statuses_last_day
        members = MEMBER_MODEL.objects.all()
        members_with_persona = [member for member in members if member.facebook_persona and member.is_current]
        members_with_feed = [member for member in members_with_persona if
                             member.facebook_persona.feeds.filter(feed_type='PP')]
        context['number_of_mks'] = len(members_with_feed)

        party_ids = [x['id'] for x in PARTY_MODEL.objects.all().values('id')]
        import random

        featured_party_id = random.choice(party_ids)
        context['featured_party'] = PARTY_MODEL.objects.get(id=featured_party_id)
        context['featured_search'] = {'search_value': u'search_str=%22%D7%A6%D7%95%D7%A0%D7%90%D7%9E%D7%99%22',
                                      'search_name': u'\u05e6\u05d5\u05e0\u05d0\u05de\u05d9'}
        max_change = Facebook_Feed.current_feeds.get_largest_fan_count_difference(POPULARITY_DIF_DAYS_BACK,
                                                                                  DEFAULT_POPULARITY_DIF_COMPARISON_TYPE,
                                                                                  MIN_FAN_COUNT_FOR_REL_COMPARISON)
        max_change['member'] = MEMBER_MODEL.objects.get(persona=max_change['feed'].persona)
        context['top_growth'] = max_change
        return context


class HotTopicsView(ListView):
    model = Tag
    template_name = 'core/hot_topics.html'

    def get_queryset(self):

        relevant_statuses = Facebook_Status.objects.filter(published__gte=(
            datetime.date.today() - datetime.timedelta(days=NUMBER_OF_LAST_DAYS_FOR_HOT_TAGS)))
        queryset = Tag.objects.filter(is_for_main_display=True,
                                      kikartags_taggeditem_items__object_id__in=[status.id for status in
                                                                                 relevant_statuses]).annotate(
            number_of_posts=Count('kikartags_taggeditem_items')).order_by(
            '-number_of_posts')[:NUMBER_OF_TAGS_TO_PRESENT]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HotTopicsView, self).get_context_data(**kwargs)
        wrote_about_tag = dict()
        for tag in context['object_list']:
            list_of_writers = Facebook_Feed.objects.filter(facebook_status__tags__id=tag.id).distinct()
            list_of_writers_with_latest_fan_count = list()
            for feed in list_of_writers:
                list_of_writers_with_latest_fan_count.append({'feed': feed,
                                                              'fan_count': feed.current_fan_count})
            sorted_list_of_writers = sorted(list_of_writers_with_latest_fan_count,
                                            key=lambda x: x['fan_count'],
                                            reverse=True)
            wrote_about_tag[tag] = [feed['feed'] for feed in sorted_list_of_writers][
                                   :NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY]
        context['wrote_about_tag'] = wrote_about_tag
        return context


class BillboardsView(ListView):
    template_name = 'core/billboards_list.html'
    model = Facebook_Feed

    stats = StatsEngine()

    def get_queryset(self, **kwargs):
        return Facebook_Feed.current_feeds.first()

    def get_context_data(self, **kwargs):
        context = super(BillboardsView, self).get_context_data(**kwargs)

        billboards = Billboards()

        context['list_of_billboards'] = []
        context['list_of_billboards'].append(billboards.number_of_followers_board)
        # context['list_of_billboards'].append(billboards.popularity_relative_growth_board)
        context['list_of_billboards'].append(billboards.popularity_growth_board)
        context['list_of_billboards'].append(billboards.number_of_status_board)
        context['list_of_billboards'].append(billboards.median_status_likes_board)
        context['list_of_billboards'].append(billboards.top_likes_board)

        context['list_of_billboards'] = sorted(context['list_of_billboards'], key=lambda x: x['order_of_board'])

        return context


class OnlyCommentsView(StatusListView):
    model = Facebook_Status
    template_name = 'core/homepage_all_statuses.html'

    def get_queryset(self):
        return self.apply_request_params(Facebook_Status.objects_no_filters.filter(is_comment=True))


class AllStatusesView(StatusListView):
    model = Facebook_Status
    template_name = 'core/homepage_all_statuses.html'
    # paginate_by = 100

    def get_queryset(self):
        retset = self.apply_request_params(super(AllStatusesView, self).get_queryset())
        # untagged url is known to be super heavy on the DB.
        # That is why it is hard coded limited to MAX_UNTAGGED matches.
        # Agam Rafaeli - 2/1/2015
        if self.request.resolver_match.url_name == "untagged":
            retset = retset[:MAX_UNTAGGED_POSTS]
        return retset

    def get_context_data(self, **kwargs):
        context = super(AllStatusesView, self).get_context_data(**kwargs)
        feeds = Facebook_Feed.objects.filter(
            facebook_status__published__gte=(
                datetime.date.today() - datetime.timedelta(hours=HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR))).distinct()
        context['side_bar_list'] = MEMBER_MODEL.objects.filter(
            id__in=[feed.persona.owner_id for feed in feeds]).distinct().order_by('name')
        context['side_bar_parameter'] = HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR
        return context


def join_queries(q1, q2, operator):
    """Join two queries with operator (e.g. or_, and_) while handling empty queries"""
    return operator(q1, q2) if (q1 and q2) else (q1 or q2)


#
class SearchView(StatusListView):
    model = Facebook_Status
    # paginate_by = 10
    context_object_name = 'filtered_statuses'
    template_name = "core/facebook_statuses_page_newdesign.html"

    def get_parsed_request(self):
        print 'request:', self.request.GET

        # adds all member ids explicitly searched for.
        members_ids = []
        if 'members' in self.request.GET.keys():
            members_ids = [int(member_id) for member_id in self.request.GET['members'].split(',')]

        # adds to member_ids all members belonging to parties explicitly searched for.
        parties_ids = []
        parties_missing_members = []
        if 'parties' in self.request.GET.keys():
            parties_ids = [int(party_id) for party_id in self.request.GET['parties'].split(',')]
            parties_missing_members = []
            parties = PARTY_MODEL.objects.filter(id__in=parties_ids)
            for party in parties:
                party_members_without_feed = []
                for member in party.current_members():
                    if Facebook_Persona.objects.filter(object_id__exact=member.id):
                        if member.id not in members_ids:
                            members_ids.append(member.id)
                    else:
                        party_members_without_feed.append(member)
                if party_members_without_feed:
                    parties_missing_members.append((party, party_members_without_feed))

        # tags searched for.
        tags_ids = []
        if 'tags' in self.request.GET.keys():
            tags_ids = [int(tag_id) for tag_id in self.request.GET['tags'].split(',')]

        # keywords searched for, comma separated
        phrases = []
        if 'search_str' in self.request.GET.keys():
            search_str_stripped = self.request.GET['search_str'].strip()[1:-1]  # removes quotes from beginning and end.
            phrases = [phrase for phrase in search_str_stripped.split('","')]

        print 'parsed request:', members_ids, parties_ids, tags_ids, phrases
        return members_ids, parties_ids, parties_missing_members, tags_ids, phrases

    def parse_q_object(self, members_ids, parties_ids, tags_ids, phrases):
        member_query = MEMBER_MODEL.objects.filter(id__in=members_ids)
        member_ids = [member.id for member in member_query]
        if IS_ELECTIONS_MODE:
            feeds = Facebook_Feed.objects.filter(persona__alt_object_id__in=member_ids)
        else:
            feeds = Facebook_Feed.objects.filter(persona__object_id__in=member_ids)

        # all members asked for (through member search of party search), with OR between them.
        members_OR_parties_Q = Q()
        if feeds:
            members_OR_parties_Q = Q(feed__in=feeds)

        # tags - search for all tags specified by their id
        tags_Q = Q()
        if tags_ids:
            # | Q(tags__synonyms__proper_form_of_tag__id=tag_id)
            tag_bundle_ids = [tag.id for tag in Tag.objects.filter_bundle(id__in=tags_ids)]
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
        for phrase in phrases:
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
        request_operator = self.request.GET.get('tags_and_search_str_operator', DEFAULT_OPERATOR)

        print 'selected_operator:', request_operator
        selected_operator = and_ if request_operator == 'and_operator' else or_

        search_str_with_tags_Q = join_queries(tags_Q, search_str_Q, selected_operator)

        print 'search_str_with_tags_Q:', search_str_with_tags_Q
        print '\n'

        query_Q = join_queries(members_OR_parties_Q, search_str_with_tags_Q, and_)

        print 'query to be executed:', query_Q
        return query_Q

    def get_queryset(self):
        members_ids, parties_ids, parties_missing_members, tags_ids, phrases = self.get_parsed_request()
        query_Q = self.parse_q_object(members_ids, parties_ids, tags_ids, phrases)
        print 'get_queryset_executed:', query_Q

        return self.apply_request_params(Facebook_Status.objects.filter(query_Q))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        members_ids, parties_ids, parties_missing_members, tags_ids, phrases = self.get_parsed_request()
        query_Q = self.parse_q_object(members_ids, parties_ids, tags_ids, phrases)
        context['members'] = MEMBER_MODEL.objects.filter(id__in=members_ids)

        context['parties'] = PARTY_MODEL.objects.filter(id__in=parties_ids)

        context['parties_missing_members'] = parties_missing_members

        context['tags'] = Tag.objects.filter(id__in=tags_ids)

        context['search_str'] = phrases
        # this is a conflict
        context['search_words'] = phrases

        context['search_title'] = 'my search'

        return_queryset = self.apply_request_params(Facebook_Status.objects.filter(query_Q))
        context['number_of_results'] = return_queryset.count()
        context['side_bar_parameter'] = HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR

        return context


class SearchGuiView(StatusListView):
    model = Facebook_Status
    template_name = "core/searchgui_page_newdesign.html"


class StatusFilterUnifiedView(StatusListView):
    model = Facebook_Status
    # paginate_by = 10
    context_object_name = 'filtered_statuses'
    page_template = "core/facebook_status_list.html"

    def get_queryset(self):
        variable_column = self.kwargs['variable_column']
        search_string = self.kwargs['id']
        if self.kwargs['context_object'] == 'tag':
            search_field = self.kwargs['search_field']
            if search_field == 'id':
                search_field = 'id'
            else:
                search_field = 'name'
                # TODO: Replace with redirect to actual url with 'name' in path, and HttpResponseRedirect()
            selected_filter = variable_column + '__' + search_field
        else:
            selected_filter = variable_column

        return self.apply_request_params(Facebook_Status.objects.filter(**{selected_filter: search_string}))

    def get_context_data(self, **kwargs):
        context = super(StatusFilterUnifiedView, self).get_context_data(**kwargs)

        object_id = self.kwargs['id']
        search_field = self.kwargs.get('search_field', 'id')
        context['object'] = self.parent_model.objects.get(**{search_field: object_id})
        return context


class MemberView(StatusFilterUnifiedView):
    template_name = "core/member.html"
    parent_model = MEMBER_MODEL

    def entry_index(request, template='myapp/entry_index.html'):
        context = {
            'entries': MemberView.objects.all(),
        }
        return render_to_response(
            template, context, context_instance=RequestContext(request))

    def get_queryset(self, **kwargs):
        self.persona = get_object_or_404(MEMBER_MODEL, id=self.kwargs['id']).facebook_persona
        if self.persona is None:
            return []
        return self.apply_request_params(self.persona.get_main_feed.facebook_status_set)

    def get_context_data(self, **kwargs):
        context = super(MemberView, self).get_context_data(**kwargs)
        stats = dict()
        if self.persona is None:  # Member with no facebook persona
            return context
        member_id = self.kwargs['id']
        feed = self.persona.get_main_feed

        dif_dict = feed.popularity_dif(POPULARITY_DIF_DAYS_BACK)
        context['change_in_popularity'] = dif_dict

        return context


class PartyView(StatusFilterUnifiedView):
    template_name = "core/party.html"
    parent_model = PARTY_MODEL

    def get_queryset(self, **kwargs):
        search_string = self.kwargs['id']
        order_by = get_order_by(self.request)
        all_members_for_party = PARTY_MODEL.objects.get(id=search_string).current_members()
        all_feeds_for_party = [member.facebook_persona.get_main_feed for member in
                               all_members_for_party if member.facebook_persona]
        date_range_Q = filter_by_date(request=self.request, datetime_field='published')
        return self.apply_request_params(
            Facebook_Status.objects.filter(feed__id__in=[feed.id for feed in all_feeds_for_party]))


class TagView(StatusFilterUnifiedView):
    template_name = "core/tag.html"
    parent_model = Tag

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        try:
            return handler(request, *args, **kwargs)
        except HasSynonymError as e:
            return HttpResponseRedirect(e.redirect_url)

    def get_queryset(self, **kwargs):
        variable_column = self.kwargs['variable_column']
        search_value = self.kwargs['id']
        search_field = self.kwargs['search_field']
        if search_field == 'id':
            search_field = 'id'
        else:
            search_field = 'name'
            # TODO: Replace with redirect to actual url with 'name' in path, and HttpResponseRedirect()
        selected_filter = variable_column + '__' + search_field

        selected_tag = Tag.objects.get(**{search_field: search_value})
        if selected_tag.synonyms.exists():
            # if has synonyms, add to queryset
            selected_filter = 'tags__in'
            search_value = [synonym.tag for synonym in selected_tag.synonyms.all()]
            search_value.append(selected_tag)  # don't forget the to add the original proper tag!

        if selected_tag.proper_form_of_tag.exists():
            # if is a synonym of another tag, redirect
            proper_tag = selected_tag.proper_form_of_tag.first().proper_form_of_tag
            url = reverse('tag', kwargs={'variable_column': 'tags',
                                         # 'context_object': 'tag',
                                         'search_field': 'id',
                                         'id': proper_tag.id})
            # return HttpResponseRedirect(url)
            raise HasSynonymError('has synonym, redirect', redirect_url=url)

        return self.apply_request_params(Facebook_Status.objects.filter(**{selected_filter: search_value}))


    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        all_feeds_for_tag = Facebook_Feed.objects.filter(
            facebook_status__id__in=[status.id for status in context['object_list']]).distinct()
        context['side_bar_list'] = MEMBER_MODEL.objects.filter(
            id__in=[feed.persona.owner_id for feed in all_feeds_for_tag]).distinct().order_by('name')
        return context


class FacebookStatusDetailView(DetailView):
    template_name = 'core/facebook_status_detail.html'

    model = Facebook_Status
    slug_field = 'status_id'

    def get_queryset(self, **kwargs):
        return Facebook_Status.objects_no_filters.filter(status_id=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super(FacebookStatusDetailView, self).get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['member'] = MEMBER_MODEL.objects.get(id=context['object'].feed.persona.owner_id)
        return context


class AllMembers(ListView):
    template_name = 'core/all_members.html'
    model = MEMBER_MODEL


class AllParties(ListView):
    template_name = 'core/all_parties.html'
    model = PARTY_MODEL


class AllTags(ListView):
    template_name = 'core/all_tags.html'
    model = Tag


class ReviewTagsView(AjaxListView):
    template_name = "core/review_tags.html"
    page_template = "core/review_tags.html"
    model = TaggedItem

    def get_queryset(self):
        queryset = TaggedItem.objects.all().order_by('-date_of_tagging')
        return queryset


# Views for getting facebook data using a user Token
def login_page(request):
    return render(request, 'core/login_page.html')


def get_data_from_facebook(request):
    """
    This Function creates or updates within our db a facebook token recieved from a user.
    After receiving the token, it is first extended into  a long-term user token
    (see https://developers.facebook.com/docs/facebook-login/access-tokens#extending for mored details)

    Next the token is saved in our db. Afterwards, the token is tested on all of our user-profile feeds, for each
    feed that the token works for, their relation will be saved in our db, for future use.

    At the end, the function redirects backwards into referrer url.
    """
    user_access_token = request.POST['access_token']
    graph = facebook.GraphAPI(access_token=user_access_token)
    # Extension into long-term token
    extended_access_token = graph.extend_access_token(settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    print 'access token, changed \nfrom: %s \nto: %s ' % (user_access_token, extended_access_token)
    graph.access_token = extended_access_token['access_token']
    # create or update token for user in db
    user = graph.get_object('me')
    token, created = User_Token.objects.get_or_create(user_id=user['id'])
    if created:
        token.token = extended_access_token['access_token']
        token.user_id = user['id']
    token.token = extended_access_token['access_token']
    token.date_of_creation = timezone.now()
    token.date_of_expiration = timezone.now() + timezone.timedelta(seconds=int(extended_access_token['expires']))
    token.save()

    # add or update relevant feeds for token
    user_profile_feeds = Facebook_Feed.objects.filter(feed_type='UP')
    # user_profile_feeds = ['508516607', '509928464']  # Used for testing
    relevant_feeds = []
    print 'checking %d user_profile feeds.' % len(user_profile_feeds)
    for i, feed in enumerate(user_profile_feeds):
        print 'working on %d of %d, vendor_id: %s.' % (i + 1, len(user_profile_feeds), feed.vendor_id)
        try:
            statuses = graph.get_connections(feed.vendor_id, 'statuses')
            if statuses['data']:
                print 'feed %s returns at least one result.' % feed
                relevant_feeds.append(feed)
        except GraphAPIError:
            print 'token not working for feed %s' % feed.vendor_id
            continue
    print 'working on %d of %d user_profile feeds.' % (len(relevant_feeds), len(user_profile_feeds))
    for feed in relevant_feeds:
        token.feeds.add(feed)
    print 'adding %d feeds to token' % len(relevant_feeds)
    token.save()
    # Redirect
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


# A handler for status_update ajax call from client
def status_update(request, status_id):
    status = Facebook_Status.objects_no_filters.get(status_id=status_id)

    response = HttpResponse(content_type="application/json", status=200)
    response_data = dict()
    response_data['id'] = status.status_id

    try:
        if status.needs_refresh:
            update_status_command = updatestatus.Command()
            update_status_command.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                                     settings.FACEBOOK_SECRET_KEY)
            status_response_dict = update_status_command.fetch_status_object_data(status_id) or {}

            response_data['likes'] = getattr(getattr(getattr(status_response_dict, 'likes', 0), 'summary', 0),
                                             'total_count', 0)
            response_data['comments'] = getattr(getattr(getattr(status_response_dict, 'comments', 0), 'summary', 0),
                                                'total_count', 0)
            response_data['shares'] = getattr(getattr(status_response_dict, 'shares', 0), 'count', 0)

            try:
                update_status_command.update_status_object_in_db(retrieved_status_data=status_response_dict,
                                                                 status_object=status,
                                                                 options={'force-update': True,
                                                                          'force-attachment-update': True})
            finally:
                response.status_code = 200


    except KeyError as e:
        response.status_code = 500

    except GraphAPIError as e:
        response.status_code = 504

    except ValueError as e:
        raise e

    except Exception as e:
        print 'status_update error:', e
        raise

    finally:
        format_int_or_null = lambda x: 0 if not x else "{:,}".format(x)

        response_data['likes'] = format_int_or_null(status.like_count)
        response_data['comments'] = format_int_or_null(status.comment_count)
        response_data['shares'] = format_int_or_null(status.share_count)
        response_data['id'] = status.status_id

        response.content = json.dumps(response_data)
        return response


# A handler for add_tag_to_status ajax call from client
@csrf_protect
def add_tag_to_status(request):
    # Todo:
    """
    1. actually restrict unregistered people from adding a tag
    2. using POST method instead of GET method
    3. using single transaction for the whole process
    """
    c = {}
    response_data = dict()
    response_data['success'] = False
    status_id = request.GET["id"]
    response_data['id'] = status_id
    tag_name = request.GET["tag_str"].strip()
    try:
        if tag_name:
            # Kikartags-based tagging
            if not re.match(TAG_NAME_REGEX, tag_name, re.UNICODE):
                response_data['error'] = 'invalid characters in tag name'
                raise Exception("Invalid characters in tag")
            taggit_tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                taggit_tag.name = tag_name
                taggit_tag.save()
            status = Facebook_Status.objects_no_filters.get(id=status_id)
            status.tags.user_aware_add(request.user, taggit_tag)
            status.save()
            response_data['tag'] = {'id': taggit_tag.id, 'name': taggit_tag.name}
            response_data['success'] = True

            # Old Deprecated Tagging
            tag, created = OldTag.objects.get_or_create(name=tag_name)
            if created:
                tag.name = tag_name
                tag.is_for_main_display = True
                tag.save()
                # add status to tag statuses
            tag.statuses.add(status_id)
            tag.save()
        else:
            response_data['success'] = True  # Nothing to do

    except Exception as e:
        print "ERROR AT ADDING STATUS TO TAG:", e
        print status_id

    finally:
        return HttpResponse(json.dumps(response_data), content_type="application/json")


# A handler for the search bar request from the client
def search_bar(request):
    search_text = request.GET['text']

    response_data = {
        'number_of_results': 0,
        'results': []
    }

    if search_text.strip():
        # factory method to create a dynamic search result

        def result_factory(object_id, name, object_type, **additional_info):
            result = {
                'id': object_id,
                'name': name,
                'type': object_type
            }
            result.update(additional_info)
            response_data['number_of_results'] += 1
            return result

        try:
            for party in search_bar_parties(search_text):
                response_data['results'].append(
                    result_factory(party.id, party.name, "party"))

            for member in search_bar_members(search_text):
                response_data['results'].append(
                    result_factory(member.id, member.name, "member", party=member.current_party.name))

            for tag in search_bar_tags(search_text):
                response_data['results'].append(
                    result_factory(tag.id, tag.name, "tag"))

        except Exception as e:
            print "search bar exception:", e
            raise

    return HttpResponse(json.dumps(response_data), content_type="application/json")


def search_bar_parties(search_text):
    query_direct_name = Q(name__contains=search_text)

    if IS_ELECTIONS_MODE:
        query_alternative_names = Q(candidatelistaltname__name__contains=search_text)
    else:
        query_alternative_names = Q(partyaltname__name__contains=search_text)

    combined_party_name_query = query_direct_name | query_alternative_names

    if IS_ELECTIONS_MODE:
        party_query = combined_party_name_query
    else:
        party_query = combined_party_name_query & Q(knesset__number=CURRENT_KNESSET_NUMBER)

    return PARTY_MODEL.objects.filter(party_query).distinct().order_by(
        'name')[:NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]


def search_bar_members(search_text):
    # Members
    query_direct_name = Q(name__contains=search_text)

    if IS_ELECTIONS_MODE:
        query_alternative_names = Q(person__personaltname__name__contains=search_text)
        combined_member_name_query = Q(person__name__contains=search_text) | query_alternative_names
        member_query = combined_member_name_query
        member_order_by = 'person__name'
    else:
        query_alternative_names = Q(memberaltname__name__contains=search_text)
        combined_member_name_query = query_direct_name | query_alternative_names
        member_query = combined_member_name_query & Q(is_current=True)
        member_order_by = 'name'

    return MEMBER_MODEL.objects.filter(member_query).distinct().select_related('current_party') \
               .order_by(member_order_by)[:NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]


def search_bar_tags(search_text):
    query_direct_name = Q(name__contains=search_text)
    query_tag_synonyms = Q(synonyms__tag__name=search_text)
    combined_tag_name_query = query_direct_name | query_tag_synonyms

    return Tag.objects.filter_proper(combined_tag_name_query).distinct().order_by('name')[
           :NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]
