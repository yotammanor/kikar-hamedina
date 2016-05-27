import random
from django.core.management.base import BaseCommand
from csv import DictWriter
from django.utils import timezone
from facebook_feeds.models import Facebook_Feed, Facebook_Status

BATCH_SIZE = 1000
SAMPLE_SIZE_FROM_BATCH = 5

START_DATE = timezone.datetime(2014, 1, 1)
END_DATE = timezone.datetime(2016, 1, 1)


class Command(BaseCommand):
    help = "Export correctly distributed Sample of Status Comments for research"
    args = '<file_name>'

    def sample(self, status, is_last, residual):
        samples_for_status = []
        comments = list(status.comments.all().values('comment_id', 'parent__status_id'))
        if residual:
            comments_and_residual = residual + comments
        else:
            comments_and_residual = comments
        num_of_full_batches = len(comments_and_residual) / BATCH_SIZE
        cut_off_point = num_of_full_batches * BATCH_SIZE
        sample_size = num_of_full_batches * SAMPLE_SIZE_FROM_BATCH
        residual = comments_and_residual[cut_off_point:]
        comments_and_residual = comments_and_residual[:cut_off_point]
        if comments_and_residual:
            try:
                samples_for_status += random.sample(comments_and_residual, sample_size)
            except ValueError:
                print(sample_size, num_of_full_batches)
                raise
        if is_last and residual:
            sample_size_from_residual = int(len(residual) / float(BATCH_SIZE) * SAMPLE_SIZE_FROM_BATCH)
            samples_for_status += random.sample(residual, sample_size_from_residual)
        return samples_for_status, residual

    def handle(self, *args, **options):
        print('Start.')
        sampled_comments = []
        feeds = Facebook_Feed.objects.all()
        for i, feed in enumerate(feeds):
            print('working on feed {} of {}'.format(i+1, feeds.count()))
            residual = None
            sampled_comments_for_feed = []
            statuses_for_feed = Facebook_Status.objects.filter(feed__id=feed.id).filter(
                published__range=[START_DATE, END_DATE]).order_by(
                'comment_count')

            for i, status in enumerate(statuses_for_feed):
                is_last = i + 1 == len(statuses_for_feed)
                samples_for_status, residual = self.sample(status, is_last, residual)
                sampled_comments_for_feed += samples_for_status

            sampled_comments += sampled_comments_for_feed
        print('total_comments:', len(sampled_comments))
        with open('sample_list.csv', 'wb') as f:
            fieldnames = ['comment_id', 'status_id']
            writer = DictWriter(f, fieldnames=fieldnames)
            writer.writerow({'comment_id': 'comment_id', 'status_id':'status_id'})
            for row in sampled_comments:
                writer.writerow({'comment_id': row['comment_id'], 'status_id': row['parent__status_id']})
        print('Done.')
