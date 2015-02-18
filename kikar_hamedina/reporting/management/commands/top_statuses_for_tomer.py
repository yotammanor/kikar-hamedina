from django.core.management.base import BaseCommand
from django.core.urlresolvers import reverse
from django.utils import timezone
from csv import DictWriter
from facebook_feeds.models import Facebook_Feed


class Command(BaseCommand):
    help = "helper script that calculates top statuses for candidates, and writes them into a csv file. Work in progress"

    def handle(self, *args, **options):

        print 'Start.'
        start_time = timezone.datetime(2014, 01, 01, 0, 0, 0, 0, tzinfo=timezone.get_current_timezone())
        end_time = timezone.datetime(2014, 11, 30, 0, 0, 0, 0, tzinfo=timezone.get_current_timezone())
        top_statuses = list()
        for feed in Facebook_Feed.objects.all():
            b = feed.facebook_status_set.filter(published__range=(start_time, end_time)).order_by('like_count').last()
            if b:
                top_statuses.append(b)

        field_names = ['member',
                       'party',
                       'status_id',
                       'published',
                       'like_count', 'share_count', 'comment_count', 'facebook_link', 'kikar_link']

        file_name = 'data_for_tomer'
        print 'Output file name:', file_name
        f = open('%s.csv' % file_name, 'wb')

        csv_data = DictWriter(f, field_names)
        headers = {field_name: field_name for field_name in field_names}
        csv_data.writerow(headers)

        for status in top_statuses:
            row_keys = headers
            row_values = [status.feed.persona.owner.name,
                          status.feed.persona.owner.current_party.name,
                          status.status_id,
                          status.published,
                          status.like_count,
                          status.share_count,
                          status.comment_count,
                          status.get_link,
                          'http://kikar.org%s' % reverse('status-detail', args=[status.status_id])]
            csv_data.writerow({x[0]: unicode(x[1]).encode('utf-8') for x in zip(row_keys, row_values)})

        f.close()
        print 'Done.'