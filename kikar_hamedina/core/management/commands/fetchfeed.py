import datetime
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import facebook
from ...models import \
    Facebook_Feed as Facebook_Feed_Model, \
    Facebook_Status as Facebook_Status_Model, \
    User_Token as User_Token_Model

DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN = 1000
DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN = 20


class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Fetches a feed'
    new_option = make_option('--initial',
                             action='store_true',
                             dest='initial',
                             default=False,
                             help='flag initial runs fql query with limit of {0} instead of regular limit of {1}'
                             .format(DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN,
                                     DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN))
    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list_helper.append(new_option)
    option_list = tuple(option_list_helper)

    graph = facebook.GraphAPI()

    def fetch_status_objects_from_feed(self, feed_id, fql_limit):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
                """
        select_self_published_status_query = """
                SELECT
                    post_id, message, created_time, like_info, comment_info, share_count, updated_time
                FROM
                    stream
                WHERE
                    source_id IN ({0}) AND actor_id IN ({0})
                LIMIT {1}""".format(feed_id, fql_limit)

        return self.graph.fql(query=select_self_published_status_query)

    def insert_status_object_to_db(self, status_object, feed_id):
        """
        Receives a single status object as retrieved from facebook-sdk, an inserts the status
        to the db.
        """
        #Create a datetime object from int received in status_object
        current_time_of_update = datetime.datetime.fromtimestamp(status_object['updated_time'],
                                                                 tz=timezone.utc)
        try:
            # If post_id already exists in DB
            status = Facebook_Status_Model.objects.get(status_id=status_object['post_id'])
            if status.updated < current_time_of_update:
                # If post_id exists but of earlier update time, fields are updated.
                status.content = status_object['message']
                status.like_count = status_object['like_info']['like_count']
                status.comment_count = status_object['comment_info']['comment_count']
                status.share_count = status_object['share_count']
                status.updated = current_time_of_update
            else:
                # If post_id exists but of equal or later time (unlikely, but may happen), disregard
                self.stdout.write('status id {0} is already up-to-date.'.format(status_object['post_id']))
        except Facebook_Status_Model.DoesNotExist:
            # If post_id does not exist at all, create it from data.
            status = Facebook_Status_Model(feed_id=feed_id,
                                           status_id=status_object['post_id'],
                                           content=status_object['message'],
                                           like_count=status_object['like_info']['like_count'],
                                           comment_count=status_object['comment_info']['comment_count'],
                                           share_count=status_object['share_count'],
                                           published=datetime.datetime.fromtimestamp(
                                               int(status_object['created_time'])),
                                           updated=current_time_of_update)
        finally:
            # save status object.
            status.save()

    def get_feed_statuses(self, feed, fql_limit):
        """
        Returns a Dict object of feed ID. and retrieved status objects.
                """
        if feed.feed_type == 'PP':
            # Set facebook graph access tokens as app access token
            self.graph.access_token = facebook.get_app_access_token(
                settings.FACEBOOK_APP_ID,
                settings.FACEBOOK_SECRET_KEY
            )
            return {'feed_id': feed.id, 'statuses': self.fetch_status_objects_from_feed(feed.vendor_id, fql_limit)}

        else:  # feed_type == 'UP' - User Profile
            # Set facebook graph access token to user access token
            token = User_Token_Model.objects.filter(feeds__id=feed.id).order_by('-date_of_creation').first()
            if not token:
                print 'No Token found for User Profile %s' % feed
                return {'feed_id': feed.id, 'statuses': []}
            else:
                print 'using token by user_id: %s' % token.user_id
                self.graph.access_token = token.token
                return {'feed_id': feed.id, 'statuses': self.fetch_status_objects_from_feed(feed.vendor_id, fql_limit)}

    def handle(self, *args, **options):
        """
        Executes fetchfeed manage.py command.
        Receives either one feed ID and retrieves Statuses for that feed,
        or no feed ID and therefore retrieves all Statuses for all the feeds.
        """
        feeds_statuses = []

        if options['initial']:
            fql_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN
        else:
            fql_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN
        print 'Variable fql_limit set to: {0}.'.format(fql_limit)

        # Case no args - fetch all feeds
        if len(args) == 0:
            for feed in Facebook_Feed_Model.objects.all():
                self.stdout.write('Working on feed: {0}.'.format(feed.pk))
                feed_statuses = self.get_feed_statuses(feed,fql_limit)
                self.stdout.write('Successfully fetched feed: {0}.'.format(feed.pk))
                for status in feed_statuses['statuses']:
                    self.insert_status_object_to_db(status, feed_statuses['feed_id'])
                self.stdout.write('Successfully written feed: {0}.'.format(feed.pk))
            self.stdout.write('Successfully fetched all')

        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])

            try:
                feed = Facebook_Feed_Model.objects.get(pk=feed_id)
                self.stdout.write('Successfully fetched feed id {0}'.format(feed_id))
            except Facebook_Feed_Model.DoesNotExist:
                raise CommandError('Feed "%s" does not exist' % feed_id)

            feed_statuses = self.get_feed_statuses(feed,fql_limit)
            for status in feed_statuses['statuses']:
                self.insert_status_object_to_db(status, feed_statuses['feed_id'])
            self.stdout.write('Successfully written feed: {0}.'.format(feed.id))

        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')



        self.stdout.write('Successfully saved all statuses to db.')
