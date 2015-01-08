from django.utils import timezone
from django.db import models
from django.conf import settings
from django_pandas.managers import DataFrameManager


class Facebook_StatusManager(DataFrameManager):
    def get_queryset(self):
        return super(Facebook_StatusManager, self).get_queryset().filter(is_comment=False).filter(feed__is_current=True)


class Facebook_FeedManager(DataFrameManager):
    def get_queryset(self):
        return super(Facebook_FeedManager, self).get_queryset().filter(is_current=True)

    def get_largest_fan_count_difference(self, days_back, comparison_type,
                                         min_fan_count_for_rel_comparison):

        current_feeds = self.get_queryset().filter(feed_type='PP')  # import pdb; pdb.set_trace()
        max_change = {'feed': None, 'dif': 0, 'day': timezone.now()}
        for feed in current_feeds:
            dif_dict = feed.popularity_dif(days_back)
            if comparison_type == 'abs':
                change_value = dif_dict['fan_count_dif_nominal']
            elif comparison_type == 'rel':
                if feed.current_fan_count <= min_fan_count_for_rel_comparison:
                    change_value = float(0)  # too small to compete in a relational context
                else:
                    change_value = dif_dict['fan_count_dif_growth_rate']
            if abs(change_value) >= abs(max_change['dif']):
                max_change['feed'] = feed
                max_change['dif'] = change_value
                max_change['day'] = dif_dict['date_of_value']
            else:
                pass

        return max_change
