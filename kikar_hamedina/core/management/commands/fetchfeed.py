import datetime

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import facebook
from ...models import Facebook_Feed as Facebook_Feed_Model, Facebook_Status as Facebook_Status_Model

# TODO: using transaction and commit once
# TODO: create only statuses which aren't shown in db
# TODO: update existing statuses


class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Fetches a feed'

    graph = facebook.GraphAPI()

    def fetch_status_objects_from_feed(self, feed_id):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
        """

        select_self_published_status_query = """
                SELECT
                    post_id, message, created_time, like_info, comment_info, share_count
                FROM
                    stream
                WHERE
                    source_id IN ({0}) AND actor_id IN ({0})""".format(feed_id)

        return self.graph.fql(query=select_self_published_status_query)

    def insert_status_object_to_db(self, status_object, feed_id):
        """
        Receives a single status object as retrieved from facebook-sdk, an inserts the status
        to the db.
        """

        Facebook_Status_Model(feed_id=feed_id,
                              status_id=status_object['post_id'],
                              content=status_object['message'],
                              like_count=status_object['like_info']['like_count'],
                              comment_count=status_object['comment_info']['comment_count'],
                              share_count=status_object['share_count'],
                              published=datetime.datetime.fromtimestamp(int(status_object['created_time']))).save()

    def get_feed_statuses(self, feed):
        """
        Returns a Dict object of feed ID. and retrieved status objects.
        """

        return {'feed_id': feed.id, 'statuses': self.fetch_status_objects_from_feed(feed.vendor_id)}

    def handle(self, *args, **options):
        """
        Executes fetchfeed manage.py command.
        Receives either one feed ID and retrieves Statuses for that feed,
        or no feed ID and therefore retrieves all Statuses for all the feeds.
        """
        feeds_statuses = []

        # Initialize facebook graph access tokens
        self.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)

        # Case no args - fetch all feeds
        if len(args) == 0:
            for feed in Facebook_Feed_Model.objects.all():
                feeds_statuses.append(self.get_feed_statuses(feed))
            self.stdout.write('Successfully fetched all')

        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])

            try:
                feed = Facebook_Feed_Model.objects.get(pk=feed_id)
                self.stdout.write('Successfully fetched feed id {0}'.format(feed_id))
            except Facebook_Feed_Model.DoesNotExist:
                raise CommandError('Feed "%s" does not exist' % feed_id)

            feeds_statuses.append(self.get_feed_statuses(feed))

        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')

        # Insert fetched statuses to database
        for feed_statuses in feeds_statuses:
            for status in feed_statuses['statuses']:
                self.insert_status_object_to_db(status, feed_statuses['feed_id'])

        self.stdout.write('Successfully saved all statuses to db.')