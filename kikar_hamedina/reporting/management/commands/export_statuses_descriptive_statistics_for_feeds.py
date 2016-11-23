#!encoding utf-8
from csv import DictWriter

import numpy as np

from django.utils import timezone

from facebook_feeds.management.commands.kikar_base_commands import KikarBaseCommand
from facebook_feeds.models import Facebook_Feed, Facebook_Status


DELIMITER = ','


class Command(KikarBaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--year',
                            action='store',
                            dest='year',
                            default=None,
                            help="choose year to filter on"
                            )

        parser.add_argument('--feed',
                            action='store',
                            dest='feed',
                            default=None,
                            help="choose year to filter on"
                            )

        parser.add_argument('--total',
                            action='store_true',
                            dest='total',
                            default=False,
                            help="Get statistics for total of activity, not separated by feed"
                            )

    def handle(self, *args, **options):
        print('Start.')
        feed = options['feed']
        feeds = Facebook_Feed.objects.filter(id=feed) if feed else Facebook_Feed.objects.all()

        file_name = 'statuses_descriptive_statistics_{}.csv'.format(timezone.now().strftime('%Y_%m_%d_%H_%M_%S'))
        with open(file_name, 'wb') as f:
            field_names = [
                'feed_id',
                'link',
                'mk_id',
                'mk_name',
                'mk_party',
                'num_of_statuses',
                'median_status_like_count',
                'mean_status_like_count',
                'median_status_comment_count',
                'mean_status_comment_count',
                'median_status_share_count',
                'mean_status_share_count',

            ]
            csv_data = DictWriter(f, fieldnames=field_names, delimiter=DELIMITER)
            headers = {field_name: field_name for field_name in field_names}
            csv_data.writerow(headers)

            for feed in feeds:
                statuses = feed.facebook_status_set_no_filters.all()
                row = {'mk_id': feed.persona.object_id,
                       'mk_name': unicode(feed.persona.content_object.name).encode(
                           'utf-8') if feed.persona.content_object else feed.username,
                       'mk_party': unicode(feed.persona.content_object.current_party.name).encode(
                           'utf-8') if feed.persona.content_object else None,
                       'feed_id': feed.id,
                       'num_of_statuses': statuses.count(),
                       'median_status_like_count': np.median(statuses.values_list('like_count', flat=True)),
                       'mean_status_like_count': np.mean(statuses.values_list('like_count', flat=True)),
                       'median_status_comment_count': np.median(statuses.values_list('comment_count', flat=True)),
                       'mean_status_comment_count': np.mean(statuses.values_list('comment_count', flat=True)),
                       'median_status_share_count': np.median(statuses.values_list('share_count', flat=True)),
                       'mean_status_share_count': np.mean(statuses.values_list('share_count', flat=True)),
                       }

                csv_data.writerow(row)
        print('Done.')
