from optparse import make_option
import logging

from django.core.management.base import BaseCommand, CommandError

from facebook_feeds.models import \
    Facebook_Feed, \
    Facebook_Status, \
    User_Token, \
    Feed_Popularity

class Command(BaseCommand):
    args = '<person_id>'
    help = 'updates_current_fan_count'

    # option_insist = make_option('-n',
    #                             '--insist',
    #                             action='store_true',
    #                             dest='is_insist',
    #                             default=False,
    #                             help='Exception from GraphAPI will result in skipping instead of crashing.'
    # )

    # option_list_helper = list()
    # for x in BaseCommand.option_list:
    #     option_list_helper.append(x)
    # option_list_helper.append(option_insist)
    # option_list = tuple(option_list_helper)

    def update_current_fan_count(self, feed):
        current_fan_count = feed.get_current_fan_count

        if current_fan_count != feed.current_fan_count:
            print 'out of date, updating'
            feed.current_fan_count = current_fan_count
            feed.save()
        else:
            print 'no update needed'

    def handle(self, *args, **options):
        """
        updates Facebook_Feed.current_fan_count field based on data of the current fan count
        within it's Feed_Popularity set.
        """

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
            # get feed properties fro, facebook
            self.update_current_fan_count(feed)
            # update fetched dat to feed in database
            # self.stdout.write('Successfully updated feed id {0}'.format(feed.id))

        self.stdout.write('Successfully saved all data in db')