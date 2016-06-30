#!encoding utf-8
from csv import DictWriter

from django.utils import timezone

from facebook_feeds.management.commands.kikar_base_commands import KikarBaseCommand
from facebook_feeds.models import Facebook_Feed, Facebook_Status_Comment

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
        languages = ['he', 'en', 'ar', 'ru', '']
        feed = options['feed']
        feeds = Facebook_Feed.objects.filter(id=feed) if feed else Facebook_Feed.objects.all()
        counter = dict()
        for feed in feeds.order_by('id'):
            print(feed.id)
            comments_for_feed = Facebook_Status_Comment.objects.filter(parent__feed__id=feed.id,
                                                                       parent__is_comment=False)
            counter[feed.id] = dict()
            counter[feed.id]['total'] = comments_for_feed.count()
            for lang in languages:
                counter[feed.id][lang] = comments_for_feed.filter(lang=lang).count()
            counter[feed.id]['other'] = comments_for_feed.exclude(lang__in=languages).count()
        file_name = 'comments_language_distribution_data_{}.csv'.format(timezone.now().strftime('%Y_%m_%d_%H_%M_%S'))
        field_names = [
                          'feed_id',
                          'link',
                          'mk_id',
                          'mk_name',
                          'mk_party',
                          'number_of_comments',
                      ] + languages
        headers = {field_name: field_name for field_name in field_names}
        with open(file_name, 'wb') as f:
            csv_data = DictWriter(f, fieldnames=field_names, delimiter=DELIMITER)
            csv_data.writerow(headers)
            for feed in feeds:
                row = {'mk_id': feed.persona.object_id,
                       'mk_name': unicode(feed.persona.content_object.name).encode(
                           'utf-8') if feed.persona.content_object else feed.username,
                       'mk_party': unicode(feed.persona.content_object.current_party.name).encode(
                           'utf-8') if feed.persona.content_object else None,
                       'feed_id': feed.id,
                       'link': 'http://www.facebook.com/{}'.format(feed.vendor_id),
                       'number_of_comments': counter[feed.id]['total'],
                       }
                for lang in languages:
                    row[lang] = counter[feed.id][lang]

                csv_data.writerow(row)
        print('Done.')
