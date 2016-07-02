import random
from django.core.management.base import BaseCommand
from csv import DictWriter
from django.utils import timezone
from facebook_feeds.models import Facebook_Feed, Facebook_Status
from optparse import make_option
import dateutil

DEFAULT_BATCH_SIZE = 200
DEFAULT_SAMPLE_SIZE_FROM_BATCH = 1

DEFAULT_FROM_DATE = "2014-01-01"
DEFAULT_TO_DATE = "2016-01-01"


class Command(BaseCommand):
    help = "Export correctly distributed Sample of Status Comments for research"
    args = '<file_name>'
    option_list = BaseCommand.option_list + (
        make_option('-b',
                    '--batch-size',
                    action='store',
                    dest='batch_size',
                    type='int',
                    default=DEFAULT_BATCH_SIZE,
                    help='set size of each sampling batch.'),
        make_option('-s',
                    '--sample-size',
                    action='store',
                    dest='sample_size',
                    type='int',
                    default=DEFAULT_SAMPLE_SIZE_FROM_BATCH,
                    help='set size of sample from each sampling batch.'),
        make_option('--from-date',
                    action='store',
                    type='string',
                    dest='from_date',
                    default=DEFAULT_FROM_DATE,
                    help='Specify date from which to sample the statuses (inclusive) e.g. 2014-03-31'),
        make_option('--to-date',
                    action='store',
                    type='string',
                    dest='to_date',
                    default=DEFAULT_TO_DATE,
                    help='Specify date until which to sample the statuses (exclusive) e.g. 2014-03-31'),
    )

    def sample(self, status, is_last, residual, sample_size, batch_size):
        samples_for_status = []
        comments = list(status.comments.all().values('comment_id', 'parent__status_id'))
        if residual:
            comments_and_residual = residual + comments
        else:
            comments_and_residual = comments
        num_of_full_batches = len(comments_and_residual) / batch_size
        cut_off_point = num_of_full_batches * batch_size
        sample_size = num_of_full_batches * sample_size
        residual = comments_and_residual[cut_off_point:]
        comments_and_residual = comments_and_residual[:cut_off_point]
        if comments_and_residual:
            try:
                samples_for_status += random.sample(comments_and_residual, sample_size)
            except ValueError:
                print(sample_size, num_of_full_batches)
                raise
        if is_last and residual:
            sample_size_from_residual = int(len(residual) / float(batch_size) * sample_size)
            samples_for_status += random.sample(residual, sample_size_from_residual)
        return samples_for_status, residual

    def handle(self, *args, **options):
        print('Start.')
        sampled_comments = []
        feeds = Facebook_Feed.objects.all()
        from_date = dateutil.parser.parse(options['from_date'])
        to_date = dateutil.parser.parse(options['to_date'])
        sample_size = options['sample_size']
        batch_size = options['batch_size']

        for i, feed in enumerate(feeds):
            print('working on feed {} of {}'.format(i + 1, feeds.count()))
            residual = None
            sampled_comments_for_feed = []
            statuses_for_feed = Facebook_Status.objects.filter(feed__id=feed.id, is_comment=False).filter(
                published__range=[from_date, to_date]).order_by(
                'comment_count')

            for i, status in enumerate(statuses_for_feed):
                is_last = i + 1 == len(statuses_for_feed)
                samples_for_status, residual = self.sample(status, is_last, residual, sample_size=sample_size,
                                                           batch_size=batch_size)
                sampled_comments_for_feed += samples_for_status

            sampled_comments += sampled_comments_for_feed
        print('total_comments:', len(sampled_comments))
        with open('{}.csv'.format(args[0]), 'wb') as f:
            fieldnames = ['comment_id', 'status_id']
            writer = DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'comment_id': 'comment_id', 'status_id': 'status_id'})
            for row in sampled_comments:
                writer.writerow({'comment_id': row['comment_id'], 'status_id': row['parent__status_id']})
        print('Done.')
