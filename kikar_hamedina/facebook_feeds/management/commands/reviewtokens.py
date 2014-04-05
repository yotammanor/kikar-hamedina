__author__ = 'yotamm'
import datetime
from optparse import make_option
from pprint import pprint
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import facebook
from ...models import \
    Facebook_Feed as Facebook_Feed_Model, \
    Facebook_Status as Facebook_Status_Model,\
    User_Token as User_Token_Model


class Command(BaseCommand):
    # args = '<person_id>'
    help = 'Checks all user tokens in db, extends their duration if possible, and reports on missing'
    graph = facebook.GraphAPI()

    def fetch_user_profile_object_by_feed_id(self, feed_id):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
        """
        pass

    def handle(self, *args, **options):
        """
        Executes reviewtokens manage.py command.

        Checks:
        1) All existing access_tokens for expiration date, returns a list of all tokens expiring soon
        2) All existing facebook_feeds, returns all feeds with no valid access token attached to.

        !This command is still non-implemented!
        """
        feeds_data = []
        # Case no args - fetch all feeds
        self.stdout.write('Empty manage command. Does Nothing')
        if len(args) == 0:
            for feed in Facebook_Feed_Model.objects.all():
                self.stdout.write('Working on feed: {0}.'.format(feed.pk))
            self.stdout.write('Successfully fetched all')

        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])

            try:
                feed = Facebook_Feed_Model.objects.get(pk=feed_id)
                self.stdout.write('Successfully fetched feed id {0}'.format(feed_id))
            except Facebook_Feed_Model.DoesNotExist:
                raise CommandError('Feed "%s" does not exist' % feed_id)

        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')

        # Update fetched data to feed in database
        for feed_data in feeds_data:
            self.update_feed_data_to_db(feed_data['data'], feed_data['feed_id'])

        self.stdout.write('Successfully saved all statuses to db.')