from ...models import Facebook_Status, Facebook_Feed
from optparse import make_option
from collections import defaultdict
from django.conf import settings
import logging
from unidecode import unidecode
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Update is_comment field for statuses'
    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list = tuple(option_list_helper)

    def update_single_status(self, status):

        value_of_is_comment = status.set_is_comment
        print 'setting value to', value_of_is_comment
        status.is_comment = value_of_is_comment
        status.save(update_fields=['is_comment'])

    def update_statuses_for_feed(self, feed):
        statuses_for_feed = Facebook_Status.objects_no_filters.filter(feed=feed)

        for status in statuses_for_feed:
            self.update_single_status(status)

    def handle(self, *args, **options):
        """
        Executes fetchfeed manage.py command.
        Receives either one feed ID and retrieves Statuses for that feed,
        or no feed ID and therefore retrieves all Statuses for all the feeds.
        """
        feeds_statuses = []

        list_of_feeds = list()
        # Case no args - fetch all feeds
        if len(args) == 0:
            list_of_feeds = [feed for feed in Facebook_Feed.objects.all()]
        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])
            try:
                feed = Facebook_Feed.objects.get(pk=feed_id)
                list_of_feeds.append(feed)
            except Facebook_Feed.DoesNotExist:
                warning_msg = "Feed #({0}) does not exist.".format(feed_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                raise CommandError('Feed "%s" does not exist' % feed_id)
        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')
        # Iterate over list_of_feeds
        for feed in list_of_feeds:
            self.stdout.write('Working on feed: {0}.'.format(feed.pk))
            self.update_statuses_for_feed(feed)
            info_msg = "Successfully updated statuses for feed: {0}.".format(feed.pk)
            logger = logging.getLogger('django')
            logger.info(info_msg)
        info_msg = "Successfully updated all statuses"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully updated all statuses.')
