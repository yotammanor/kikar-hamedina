import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import facebook
from ...models import Facebook_Feed as facebook_feed_model, Facebook_Status as facebook_status_model

# TODO: using transaction and commit once
# TODO: create only statuses which aren't shown in db
# TODO: update existing statuses


class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Fetches a feed'

    graph = facebook.GraphAPI()

    def fetch_statuses_from_feed(self, feed_id):
        query = """SELECT post_id, message, created_time, like_info, comment_info, share_count
                   FROM stream
                   WHERE source_id IN ({0}) AND actor_id IN ({0})""".format(feed_id)

        return self.graph.fql(query=query)

    def insert_status_post_to_db(self, status_object, feed_id):
        facebook_status_model(feed_id = feed_id,
                              status_id=status_object['post_id'],
                              content=status_object['message'],
                              like_count=status_object['like_info']['like_count'],
                              comment_count=status_object['comment_info']['comment_count'],
                              share_count=status_object['share_count'],
                              published=datetime.datetime.fromtimestamp(int(status_object['created_time']))).save()

    def get_feed_statuses(self, feed):
        return {'feed_id': feed.id, 'statuses': self.fetch_statuses_from_feed(feed.vendor_id)}

    def handle(self, *args, **options):
        feeds_statuses = []

        self.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)

        if len(args) == 0:
            for feed in facebook_feed_model.objects.all():
                feeds_statuses.append(self.get_feed_statuses(feed))

        elif len(args) == 1:
            feed_id = int(args[0])

            try:
                feed = facebook_feed_model.objects.get(pk=feed_id)
            except facebook_feed_model.DoesNotExist:
                raise CommandError('Feed "%s" does not exist' % feed_id)

            feeds_statuses.append(self.get_feed_statuses(feed))

        else:
            raise CommandError('Please enter an id')

        # Insert to databse
        for feed_statuses in feeds_statuses:
            for status in feed_statuses['statuses']:
                self.insert_status_post_to_db(status, feed_statuses['feed_id'])

        self.stdout.write('Successfully fetched all')