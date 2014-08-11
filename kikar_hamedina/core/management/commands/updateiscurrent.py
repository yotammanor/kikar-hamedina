from optparse import make_option
from pprint import pprint
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from mks.models import Member
from facebook_feeds.models import Facebook_Feed


class Command(BaseCommand):
    args = '<feed_id>'
    help = "updates facebook_feed's is_current field"

    set_value_manually = make_option('-m',
                                     '--set-value-manually',
                                     action='store',
                                     dest='set-value-manually',
                                     help='set value of is_current field manualy. usage -m=True')

    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list_helper.append(set_value_manually)
    option_list = tuple(option_list_helper)

    def decide_is_current_field(self, feed, options):
        is_current_value = bool
        related_member = Member.objects.get(pk=feed.persona.object_id)

        if options['set-value-manually']:
            try:
                is_current_value = eval(options['set-value-manually'])
            except KeyError:
                use_manual_value = False
            except NameError:
                warning_msg = "manual input ({0}) is incorrect.".format(options['set-value-manually'])
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                raise CommandError('manual input "%s" is incorrect, use True or False' % options['set-value-manually'])

        elif related_member:
            is_current_value = related_member.is_current
        else:
            # Feed unattached to mk is set to be non-current by default
            is_current_value = False

        print 'is_current_value for feed %s is set to: %s' %(feed, is_current_value)
        return is_current_value

    def handle(self, *args, **options):
        """
        This commands sets facebook_feed.is_current field value to either True or False
        Updates data in facebook feeds according to information from mks, or with manual input.

        """
        feeds_for_update = []
        # Case no args - fetch all feeds
        if len(args) == 0:
            feeds_for_update = [feed for feed in Facebook_Feed.objects.all()]

        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = args[0]
            try:
                feed = Facebook_Feed.objects.get(id=feed_id)
                feeds_for_update.append(feed)

            except Facebook_Feed.DoesNotExist:
                warning_msg = "Feed #({0}) does not exist.".format(feed_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                raise CommandError('Feed "%s" does not exist' % feed_id)

        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')

        # Update fetched data to feed in database
        for feed in feeds_for_update:
            is_current_value = self.decide_is_current_field(feed, options)
            feed.is_current = is_current_value
            feed.save()

        self.stdout.write('Successfully updated all feeds.')
