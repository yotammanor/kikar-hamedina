import datetime
import time
import urllib2
import json
from operator import or_, and_
from IPython.lib.pretty import pprint
from collections import defaultdict

from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import FieldError, ObjectDoesNotExist
from django.shortcuts import render, render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseServerError, Http404
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.base import View
from django.template import RequestContext
from django.utils import timezone
from django.db.models import Count, Q, Max, F
from django.conf import settings
from django import db

import facebook
from endless_pagination.views import AjaxListView

from facebook_feeds.models import Facebook_Status, Facebook_Feed, Tag, User_Token, Feed_Popularity
from facebook_feeds.management.commands import updatestatus
from mks.models import Party, Member
from facebook import GraphAPIError
from core.insights import StatsEngine

# current knesset number
CURRENT_KNESSET_NUMBER = getattr(settings, 'CURRENT_KNESSET_NUMBER', 19)

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

TAGS_FROM_LAST_DAYS = 7

NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR = 3


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


def get_order_by(request):
    """
    This function receives a request, and parses order_by parameter, if exits into
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

    print filter_range_arg

    date_time_field_range = datetime_field + '__range'
    range_value = (start_date, end_date)
    return Q(**{date_time_field_range: range_value})


class StatusListView(AjaxListView):
    page_template = "core/facebook_status_list.html"

    def apply_reqest_params(self, query):
        """Apply request params to DB query. This currently includes 'range'
        and 'order_by' """
        date_range_Q = filter_by_date(self.request)
        result = query.filter(date_range_Q)

        order_by = get_order_by(self.request)
        if order_by:
            # By default ordering puts NULLs on top, but we want them in the
            # bottom. It isn't trivial to change this behavior in django
            # (more so for non-fixed fields) but important for user experience
            # See http://stackoverflow.com/q/7749216
            null_field = order_by[0]
            if null_field.startswith('-'):
                null_field = null_field[1:]
                null_order = 'is_null'
            else:
                null_order = '-is_null'
            # We need to be paranoid here with raw SQL escaping, as there is
            # no standard way to escape field name (select_params is only for
            # values, not names). So only fix NULLs for these specific fields.
            # See http://stackoverflow.com/q/6618344
            if null_field in ("published", "like_count", "comment_count"):
                result = result.extra(select={'is_null': '%s IS NULL' % null_field}).order_by(null_order, *order_by)
            else:
                result = result.order_by(*order_by)
        return result


class HomepageView(ListView):
    template_name = 'core/homepage.html'
    model = Facebook_Status

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        new_statuses_last_day = Facebook_Status.objects.filter(published__gte=(
            datetime.date.today() - datetime.timedelta(days=1))).count()
        context['statuses_last_day'] = new_statuses_last_day
        members = Member.objects.filter(is_current=True)
        members_with_persona = [member for member in members if member.facebook_persona]
        members_with_feed = [member for member in members_with_persona if member.facebook_persona.feeds.all()]
        context['number_of_mks'] = len(members_with_feed)
        context['featured_party'] = Party.objects.get(id=16)
        context['featured_search'] = {'search_value': u'search_str=%22%D7%A6%D7%95%D7%A0%D7%90%D7%9E%D7%99%22',
                                      'search_name': u'\u05e6\u05d5\u05e0\u05d0\u05de\u05d9'}
        max_change = Facebook_Feed.current_feeds.get_largest_fan_count_difference(POPULARITY_DIF_DAYS_BACK,
                                                                                  DEFAULT_POPULARITY_DIF_COMPARISON_TYPE,
                                                                                  MIN_FAN_COUNT_FOR_REL_COMPARISON)
        max_change['member'] = Member.objects.get(persona=max_change['feed'].persona)
        context['top_growth'] = max_change
        return context


class HotTopicsView(ListView):
    model = Tag
    template_name = 'core/homepage_old.html'

    def get_queryset(self):
        queryset = Tag.objects.filter(is_for_main_display=True, statuses__published__gte=(
            datetime.date.today() - datetime.timedelta(days=TAGS_FROM_LAST_DAYS))).annotate(
            number_of_posts=Count('statuses')).order_by(
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

    def create_billboard_data_dict_list(self,
                                        value_format,
                                        data_set,
                                        data_name_attr,
                                        data_value_int_attr,
                                        calc_type,
                                        arguments_for_function,
                                        link_value_attr):

        if calc_type == 'function':
            data_dict_list = [
                {'name': getattrd(object_instance, data_name_attr),
                 'value_int': float(getattrd(object_instance, data_value_int_attr)(**arguments_for_function) or 0),
                 'value_formatted': value_format.format(
                     getattrd(object_instance, data_value_int_attr)(**arguments_for_function) or 0),
                 'value_reference_link': getattrd(object_instance, link_value_attr),
                }
                for object_instance in data_set
            ]

        elif calc_type == 'stats':

            stats_method = getattrd(self.stats, data_value_int_attr)

            data_dict_list = [
                {'name': getattrd(object_instance, data_name_attr),
                 'value_int': float(stats_method([object_instance.id]) or 0),
                 'value_formatted': value_format.format(stats_method([object_instance.id]) or 0),
                 'value_reference_link': getattrd(object_instance, link_value_attr),
                }
                for object_instance in data_set
            ]
        else:
            # calc_type == 'attribute':
            data_dict_list = [
                {'name': getattrd(object_instance, data_name_attr),
                 'value_int': float(getattrd(object_instance, data_value_int_attr)),
                 'value_formatted': value_format.format(getattrd(object_instance, data_value_int_attr)),
                 'value_reference_link': getattrd(object_instance, link_value_attr),
                }
                for object_instance in data_set
            ]

        return data_dict_list

    def create_billboard_dict(self,
                              title,
                              header_name,
                              header_value_formatted,
                              link_uri_name,
                              value_format,
                              data_set,
                              data_name_attr,
                              data_value_float_attr,
                              top_num_of_values,
                              calc_type,
                              link_value_attr,
                              arguments_for_function=None,
                              is_sorted_reversed=True):
        billboard_dict = {
            'title': title,
            'headers': {
                'name': header_name,
                'value_formatted': header_value_formatted,
            },
            'link_uri_name': link_uri_name,
            'data': self.create_billboard_data_dict_list(value_format,
                                                         data_set,
                                                         data_name_attr,
                                                         data_value_float_attr,
                                                         calc_type,
                                                         arguments_for_function,
                                                         link_value_attr),
        }

        billboard_dict['data'] = sorted(billboard_dict['data'], key=lambda x: x['value_int'],
                                        reverse=is_sorted_reversed)[
                                 :top_num_of_values]

        return billboard_dict

    def get_context_data(self, **kwargs):
        context = super(BillboardsView, self).get_context_data(**kwargs)

        billboard_1 = self.create_billboard_dict(title='popularity',
                                                 header_name='Name',
                                                 header_value_formatted='current_fan_count',
                                                 link_uri_name='member',
                                                 value_format="{:,}",
                                                 top_num_of_values=10,
                                                 is_sorted_reversed=True,
                                                 data_set=Facebook_Feed.current_feeds.all(),
                                                 data_name_attr='persona.content_object.name',
                                                 data_value_float_attr='current_fan_count',
                                                 link_value_attr='persona.object_id',
                                                 calc_type='attribute',
                                                 arguments_for_function=None,
        )

        billboard_2 = self.create_billboard_dict(title='popularity_growth',
                                                 header_name='Name',
                                                 header_value_formatted='growth popularity',
                                                 link_uri_name='member',
                                                 value_format="{:.2%}",
                                                 top_num_of_values=10,
                                                 is_sorted_reversed=True,
                                                 data_set=Facebook_Feed.current_feeds.filter(feed_type='PP'),
                                                 data_name_attr='persona.content_object.name',
                                                 data_value_float_attr='popularity_dif',
                                                 link_value_attr='persona.object_id',
                                                 calc_type='function',
                                                 arguments_for_function={'days_back': 7,
                                                                         'return_value': 'fan_count_dif_growth_rate'},
        )

        billboard_3 = self.create_billboard_dict(title='popularity_growth_nominal',
                                                 header_name='Name',
                                                 header_value_formatted='growth in popularity (likes)',
                                                 link_uri_name='member',
                                                 value_format="{:,.0f}",
                                                 top_num_of_values=10,
                                                 is_sorted_reversed=True,
                                                 data_set=Facebook_Feed.current_feeds.all(),
                                                 data_name_attr='persona.content_object.name',
                                                 data_value_float_attr='popularity_dif',
                                                 link_value_attr='persona.object_id',
                                                 calc_type='function',
                                                 arguments_for_function={'days_back': 7,
                                                                         'return_value': 'fan_count_dif_nominal'},
        )

        billboard_4 = self.create_billboard_dict(title='num_of_statuses',
                                                 header_name='Name',
                                                 header_value_formatted='number of statuses last month',
                                                 link_uri_name='member',
                                                 value_format="{:,.0f}",
                                                 top_num_of_values=10,
                                                 is_sorted_reversed=True,
                                                 data_set=Facebook_Feed.current_feeds.all(),
                                                 data_name_attr='persona.content_object.name',
                                                 data_value_float_attr='n_statuses_last_month',
                                                 link_value_attr='persona.object_id',
                                                 calc_type='stats',
                                                 arguments_for_function=None,
        )

        billboard_5 = self.create_billboard_dict(title='mean_status_likes_last_month',
                                                 header_name='Name',
                                                 header_value_formatted='mean_status_likes_last_month',
                                                 link_uri_name='member',
                                                 value_format="{:,.0f}",
                                                 top_num_of_values=10,
                                                 is_sorted_reversed=True,
                                                 data_set=Facebook_Feed.current_feeds.all(),
                                                 data_name_attr='persona.content_object.name',
                                                 data_value_float_attr='mean_status_likes_last_month',
                                                 link_value_attr='persona.object_id',
                                                 calc_type='stats',
                                                 arguments_for_function=None,
        )

        # billboard_6 = self.create_billboard_dict(title='Most popular status',
        # header_name='Name',
        # header_value_formatted='likes for most popular status',
        # value_format="{:,.0f}",
        # top_num_of_values=10,
        # is_sorted_reversed=True,
        # data_set=self.stats.popular_statuses_last_month(
        # [feed.id for feed in Facebook_Feed.current_feeds.all()], 10),
        # data_name_attr='persona.content_object.name',
        # data_value_float_attr='mean_status_likes_last_month',
        # calc_type='stats',
        # arguments_for_function=None,
        # )

        billboard_6 = {
            'title': 'Most popular status this Month',
            'headers': {
                'name': 'Name',
                'value_formatted': 'likes for most popular status'
            },
            'link_uri_name': 'status-detail',
            'data': [
                {'name': Facebook_Status.objects.get(id=result_array[0]).feed.persona.content_object.name,
                 'value_int': float(result_array[1]),
                 'value_formatted': "{:,.0f}".format(result_array[1]),
                 'value_reference_link': Facebook_Status.objects.get(id=result_array[0]).status_id,
                }
                for result_array in self.stats.popular_statuses_last_month(
                    [feed.id for feed in Facebook_Feed.current_feeds.all()], 10)
            ]
        }

        context['list_of_billboards'] = []
        context['list_of_billboards'].append(billboard_1)
        context['list_of_billboards'].append(billboard_2)
        context['list_of_billboards'].append(billboard_3)
        context['list_of_billboards'].append(billboard_4)
        context['list_of_billboards'].append(billboard_5)
        context['list_of_billboards'].append(billboard_6)

        return context


class OnlyCommentsView(StatusListView):
    model = Facebook_Status
    template_name = 'core/all_results.html'

    def get_queryset(self):
        return self.apply_reqest_params(Facebook_Status.objects_no_filters.filter(is_comment=True))


class AllStatusesView(StatusListView):
    model = Facebook_Status
    template_name = 'core/all_results.html'
    # paginate_by = 100

    def get_queryset(self):
        return self.apply_reqest_params(super(AllStatusesView, self).get_queryset())

    def get_context_data(self, **kwargs):
        context = super(AllStatusesView, self).get_context_data(**kwargs)
        feeds = Facebook_Feed.objects.filter(
            facebook_status__published__gte=(
                datetime.date.today() - datetime.timedelta(hours=HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR))).distinct()
        context['side_bar_list'] = Member.objects.filter(
            id__in=[feed.persona.object_id for feed in feeds]).distinct().order_by('name')
        context['side_bar_parameter'] = HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR
        return context


#
class SearchView(StatusListView):
    model = Facebook_Status
    # paginate_by = 10
    context_object_name = 'filtered_statuses'
    template_name = "core/search.html"

    def get_parsed_request(self):
        print 'request:', self.request.GET

        # adds all member ids explicitly searched for.
        members_ids = []
        if 'members' in self.request.GET.keys():
            members_ids = [int(member_id) for member_id in self.request.GET['members'].split(',')]

        # adds to member_ids all members belonging to parties explicitly searched for.
        parties_ids = []
        if 'parties' in self.request.GET.keys():
            parties_ids = [int(party_id) for party_id in self.request.GET['parties'].split(',')]
            parties = Party.objects.filter(id__in=parties_ids)
            for party in parties:
                for member in party.current_members():
                    if member.id not in members_ids:
                        members_ids.append(member.id)

        # tags searched for.
        tags_ids = []
        if 'tags' in self.request.GET.keys():
            tags_ids = [int(tag_id) for tag_id in self.request.GET['tags'].split(',')]

        # keywords searched for, comma separated
        words = []
        if 'search_str' in self.request.GET.keys():
            search_str_stripped = self.request.GET['search_str'].strip()[1:-1]  # removes quotes from beginning and end.
            words = [word for word in search_str_stripped.split('","')]

        print 'parsed request:', members_ids, parties_ids, tags_ids, words
        return members_ids, parties_ids, tags_ids, words

    def parse_q_object(self, members_ids, parties_ids, tags_ids, words):
        member_query = Member.objects.filter(id__in=members_ids)
        feeds = Facebook_Feed.objects.filter(persona__object_id__in=[member.id for member in member_query])

        # all members asked for (through member search of party search), with OR between them.
        memebers_OR_parties_Q = Q()
        if feeds:
            memebers_OR_parties_Q = Q(feed__in=feeds)

        # tags - search for all tags specified by their id
        tags_Q = Q()
        if tags_ids:
            tags_to_queries = [Q(tags__id=tag_id) for tag_id in tags_ids]
            print 'tags_to_queries:', len(tags_to_queries)
            for query_for_single_tag in tags_to_queries:
                # print 'Now adding query:', query_for_single_tag
                if not tags_Q:
                    # the first query overrides the empty concatenated query
                    tags_Q = query_for_single_tag
                else:
                    # the rest are concatenated with OR
                    tags_Q = query_for_single_tag | tags_Q
        else:
            tags_Q = Q()

        print 'tags_Q:', tags_Q

        # keywords - searched both in content and in tags of posts.
        search_str_Q = Q()
        for word in words:
            if not search_str_Q:
                search_str_Q = Q(content__contains=word)
                search_str_Q = Q(tags__name__contains=word) | search_str_Q
            else:
                search_str_Q = Q(content__contains=word) | search_str_Q
                search_str_Q = Q(tags__name__contains=word) | search_str_Q

        # tags query and keyword query concatenated. Logic is set according to request input
        try:
            request_operator = self.request.GET['tags_and_search_str_operator']
        except MultiValueDictKeyError:
            request_operator = DEFAULT_OPERATOR

        print 'selected_operator:', request_operator
        if request_operator == 'or_operator':
            selected_operator = or_
        else:
            selected_operator = and_

        # Handle joining of empty queries
        search_str_with_tags_Q = Q()
        if tags_Q and search_str_Q:
            search_str_with_tags_Q = selected_operator(tags_Q, search_str_Q)
        elif tags_Q:
            search_str_with_tags_Q = tags_Q
        elif search_str_Q:
            search_str_with_tags_Q = search_str_Q

        print 'search_str_with_tags_Q:', search_str_with_tags_Q
        print '\n'
        # print 'members_or_parties:', memebers_OR_parties_Q, bool(memebers_OR_parties_Q)
        # print 'keywords_or_tags:', search_str_with_tags_Q, bool(search_str_with_tags_Q)

        query_Q = Q()
        if memebers_OR_parties_Q and search_str_with_tags_Q:
            query_Q = memebers_OR_parties_Q & search_str_with_tags_Q
        elif memebers_OR_parties_Q:
            query_Q = memebers_OR_parties_Q
        elif search_str_with_tags_Q:
            query_Q = search_str_with_tags_Q

        print 'query to be executed:', query_Q
        return query_Q

    def get_queryset(self):
        members_ids, parties_ids, tags_ids, words = self.get_parsed_request()
        query_Q = self.parse_q_object(members_ids, parties_ids, tags_ids, words)
        print 'get_queryset_executed:', query_Q

        return self.apply_reqest_params(Facebook_Status.objects.filter(query_Q))

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)

        members_ids, parties_ids, tags_ids, words = self.get_parsed_request()
        query_Q = self.parse_q_object(members_ids, parties_ids, tags_ids, words)
        context['members'] = Member.objects.filter(id__in=members_ids)

        context['parties'] = Party.objects.filter(id__in=parties_ids)

        context['tags'] = Tag.objects.filter(id__in=tags_ids)

        context['search_str'] = words

        context['search_title'] = 'my search'

        return_queryset = self.apply_reqest_params(Facebook_Status.objects.filter(query_Q))
        context['number_of_results'] = return_queryset.count()
        context['side_bar_parameter'] = HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR

        return context


class SearchGuiView(StatusListView):
    model = Facebook_Status
    template_name = "core/searchgui.html"


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

        return self.apply_reqest_params(Facebook_Status.objects.filter(**{selected_filter: search_string}))

    def get_context_data(self, **kwargs):
        context = super(StatusFilterUnifiedView, self).get_context_data(**kwargs)

        object_id = self.kwargs['id']
        search_field = self.kwargs.get('search_field', 'id')
        context['object'] = self.parent_model.objects.get(**{search_field: object_id})
        return context


class MemberView(StatusFilterUnifiedView):
    template_name = "core/member.html"
    parent_model = Member

    def entry_index(request, template='myapp/entry_index.html'):
        context = {
            'entries': MemberView.objects.all(),
        }
        return render_to_response(
            template, context, context_instance=RequestContext(request))

    def get_queryset(self, **kwargs):
        search_string = self.kwargs['id']

        self.persona = get_object_or_404(Member, id=search_string).facebook_persona
        if self.persona is None:
            return []

        return self.apply_reqest_params(self.persona.get_main_feed.facebook_status_set)

    def get_context_data(self, **kwargs):
        context = super(MemberView, self).get_context_data(**kwargs)
        stats = dict()
        if self.persona is None:  # Member with no facebook persona
            return context
        member_id = self.kwargs['id']
        feed = Facebook_Feed.objects.get(persona__object_id=member_id)

        dif_dict = feed.popularity_dif(POPULARITY_DIF_DAYS_BACK)
        context['change_in_popularity'] = dif_dict

        return context


class PartyView(StatusFilterUnifiedView):
    template_name = "core/party.html"
    parent_model = Party

    def get_queryset(self, **kwargs):
        search_string = self.kwargs['id']
        order_by = get_order_by(self.request)
        all_members_for_party = Party.objects.get(id=search_string).current_members()
        all_feeds_for_party = [member.facebook_persona.get_main_feed for member in
                               all_members_for_party if member.facebook_persona]
        date_range_Q = filter_by_date(request=self.request, datetime_field='published')
        return self.apply_reqest_params(
            Facebook_Status.objects.filter(feed__id__in=[feed.id for feed in all_feeds_for_party]))


class TagView(StatusFilterUnifiedView):
    template_name = "core/tag.html"
    parent_model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        print context['object_list']
        all_feeds_for_tag = Facebook_Feed.objects.filter(
            facebook_status__id__in=[status.id for status in context['object_list']]).distinct()
        context['side_bar_list'] = Member.objects.filter(
            id__in=[feed.persona.object_id for feed in all_feeds_for_tag]).distinct().order_by('name')
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
        context['member'] = Member.objects.get(id=context['object'].feed.persona.object_id)
        return context


class AllMembers(ListView):
    template_name = 'core/all_members.html'
    model = Member


class AllParties(ListView):
    template_name = 'core/all_parties.html'
    model = Party


class AllTags(ListView):
    template_name = 'core/all_tags.html'
    model = Tag


def about_page(request):
    return render(request, 'core/about.html')


def add_tag(request, id):
    status = Facebook_Status.objects.get(id=id)
    tagsString = request.POST['tag']
    tagsList = tagsString.split(',')
    for tagName in tagsList:
        strippedTagName = tagName.strip()
        if strippedTagName:
            tag, created = Tag.objects.get_or_create(name=strippedTagName)
            if created:
                tag.name = strippedTagName
                tag.is_for_main_display = True
                tag.save()
                # add status to tag statuses
            tag.statuses.add(status)
            tag.save()

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


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
    status = Facebook_Status.objects.get(status_id=status_id)

    response = HttpResponse(content_type="application/json")
    response_data = dict()
    response_data['id'] = status.status_id

    try:

        update_status_command = updatestatus.Command()
        update_status_command.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                                 settings.FACEBOOK_SECRET_KEY)
        status_response_dict = update_status_command.fetch_status_object_data(status_id)

        response_data['likes'] = getattr(getattr(getattr(status_response_dict, 'likes', None), 'summary', None),
                                         'total_count', None)
        response_data['comments'] = getattr(getattr(getattr(status_response_dict, 'comments', None), 'summary', None),
                                            'total_count', None)
        response_data['shares'] = getattr(getattr(status_response_dict, 'shares', None), 'count', None)
        try:
            status.like_count = int(response_data['likes'])
            status.comment_count = int(response_data['comments'])
            status.share_count = int(response_data['shares'])
            status.save()
            # print 'saved data to db'
        finally:
            format_int_or_null = lambda x: 0 if not x else "{:,}".format(x)

            response_data['likes'] = format_int_or_null(status.like_count)
            response_data['comments'] = format_int_or_null(status.comment_count)
            response_data['shares'] = format_int_or_null(status.share_count)
            response_data['id'] = status.status_id
            response.status_code = 200

    except KeyError as e:
        response.status_code = 500

    except GraphAPIError as e:
        response.status_code = 504

    except ValueError as e:
        raise e

    finally:
        # print 'response is:', response_data
        response.content = json.dumps(response_data)
        return response


# A handler for add_tag_to_status ajax call from client
def add_tag_to_status(request):
    response_data = dict()
    response_data['success'] = False
    status_id = request.GET["id"]
    response_data['id'] = status_id
    tagName = request.GET["tag_str"]
    strippedTagName = tagName.strip()
    try:
        if strippedTagName:
            tag, created = Tag.objects.get_or_create(name=strippedTagName)
            if created:
                tag.name = strippedTagName
                tag.is_for_main_display = True
                tag.save()
                # add status to tag statuses
            tag.statuses.add(status_id)
            tag.save()
            response_data['tag'] = {'id': tag.id, 'name': tag.name}
        response_data['success'] = True
    except:
        print "ERROR AT ADDING STATUS TO TAG"
        print status_id

    finally:
        return HttpResponse(json.dumps(response_data), content_type="application/json")


# A handler for the search bar request from the client
def search_bar(request):
    searchText = request.GET['text']

    response_data = {
        'number_of_results': 0,
        'results': []
    }

    if searchText.strip():
        # factory method to create a dynamic search result
        def result_factory(id, name, type, **additional_info):
            result = {
                'id': id,
                'name': name,
                'type': type
            }
            result.update(additional_info)
            response_data['number_of_results'] += 1
            return result

        members = Member.objects.filter(name__contains=searchText, is_current=True) \
                      .select_related('current_party').order_by('name')[:NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]
        for member in members:
            response_data['results'].append(
                result_factory(member.id, member.name, "member", party=member.current_party.name))

        tags = Tag.objects.filter(name__contains=searchText).order_by('name')[:NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]
        for tag in tags:
            response_data['results'].append(
                result_factory(tag.id, tag.name, "tag"))

        parties = Party.objects.filter(name__contains=searchText, knesset__number=CURRENT_KNESSET_NUMBER).order_by(
            'name')[
                  :NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]
        for party in parties:
            response_data['results'].append(
                result_factory(party.id, party.name, "party"))

    return HttpResponse(json.dumps(response_data), content_type="application/json")
