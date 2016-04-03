# -*- coding: utf-8 -*-
from facebook_feeds.models import Facebook_Feed, Facebook_Status
from core.insights import StatsEngine
from django.utils.translation import ugettext_lazy as _

from core.utils import getattrd

TOP_NUM_OF_VALUES = 10
DAYS_BACK = 14
DEFAULT_SECOND_TITLE = _('Last Two Weeks')


class Billboards(object):
    def __init__(self):
        self.stats = StatsEngine()
        self.number_of_followers_board = self.create_billboard_dict(title=_('Number of Followers'),
                                                                    second_title=_('Total'),
                                                                    header_name=_('MK'),
                                                                    header_value_formatted='current_fan_count',
                                                                    link_uri_name='member',
                                                                    value_format="{:,}",
                                                                    top_num_of_values=TOP_NUM_OF_VALUES,
                                                                    is_sorted_reversed=True,
                                                                    data_set=Facebook_Feed.current_feeds.all(),
                                                                    data_name_attr='persona.owner.name',
                                                                    data_value_float_attr='current_fan_count',
                                                                    link_value_attr='persona.owner_id',
                                                                    calc_type='attribute',
                                                                    arguments_for_function=None,
                                                                    order_of_board=6,
                                                                    )

        self.popularity_growth_board = self.create_billboard_dict(title=_('Growth in Number of Followers'),
                                                                  second_title=DEFAULT_SECOND_TITLE,
                                                                  header_name='Name',
                                                                  header_value_formatted='growth in popularity (likes)',
                                                                  link_uri_name='member',
                                                                  value_format="{:,.0f}",
                                                                  top_num_of_values=TOP_NUM_OF_VALUES,
                                                                  is_sorted_reversed=True,
                                                                  data_set=Facebook_Feed.current_feeds.all(),
                                                                  data_name_attr='persona.owner.name',
                                                                  data_value_float_attr='popularity_dif',
                                                                  link_value_attr='persona.owner_id',
                                                                  calc_type='function',
                                                                  arguments_for_function={'days_back': DAYS_BACK,
                                                                                          'return_value': 'fan_count_dif_nominal'},
                                                                  order_of_board=2,
                                                                  )

        self.number_of_status_board = self.create_billboard_dict(title=_('Number of Statuses Published'),
                                                                 second_title=DEFAULT_SECOND_TITLE,
                                                                 header_name='Name',
                                                                 header_value_formatted='number of statuses last week',
                                                                 link_uri_name='member',
                                                                 value_format="{:,.0f}",
                                                                 top_num_of_values=TOP_NUM_OF_VALUES,
                                                                 is_sorted_reversed=True,
                                                                 data_set=Facebook_Feed.current_feeds.all(),
                                                                 data_name_attr='persona.owner.name',
                                                                 data_value_float_attr='n_statuses_last_week',
                                                                 link_value_attr='persona.owner_id',
                                                                 calc_type='stats',
                                                                 arguments_for_function=None,
                                                                 order_of_board=3,
                                                                 )

        self.median_status_likes_board = self.create_billboard_dict(title=_('Median #like Count per Status'),
                                                                    second_title=DEFAULT_SECOND_TITLE,
                                                                    header_name='Name',
                                                                    header_value_formatted='median_status_likes_last_week',
                                                                    link_uri_name='member',
                                                                    value_format="{:,.0f}",
                                                                    top_num_of_values=TOP_NUM_OF_VALUES,
                                                                    is_sorted_reversed=True,
                                                                    data_set=Facebook_Feed.current_feeds.all(),
                                                                    data_name_attr='persona.owner.name',
                                                                    data_value_float_attr='median_status_likes_last_week',
                                                                    link_value_attr='persona.owner_id',
                                                                    calc_type='stats',
                                                                    arguments_for_function=None,
                                                                    order_of_board=4,
                                                                    )

        self.top_likes_board = {
            'order_of_board': 5,
            'title': _('Top Statuses by Number of  #like '),
            'second_title': _('Last Week'),
            'headers': {
                'name': 'Name',
                'value_formatted': 'likes for most popular status'
            },
            'link_uri_name': 'status-detail',
            'data': [
                {'name': Facebook_Status.objects.get(id=result_array[0]).feed.persona.owner.name,
                 'value_int': float(result_array[1]),
                 'value_formatted': "{:,.0f}".format(result_array[1]),
                 'value_reference_link': Facebook_Status.objects.get(id=result_array[0]).status_id,
                 }
                for result_array in self.stats.popular_statuses_last_week(
                        [feed.id for feed in Facebook_Feed.current_feeds.all()], TOP_NUM_OF_VALUES)
                ]
        }

    def create_billboard_dict(self,
                              order_of_board,
                              title,
                              second_title,
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
            'order_of_board': order_of_board,
            'title': title,
            'second_title': second_title,
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
