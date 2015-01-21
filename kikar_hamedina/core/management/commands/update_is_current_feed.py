from optparse import make_option
from pprint import pprint
import logging

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from mks.models import Member
from persons.models import Person
from polyorg.models import Candidate
from facebook_feeds.models import Facebook_Feed, Facebook_Persona

IS_ELECTIONS_MODE = getattr(settings, 'IS_ELECTIONS_MODE', False)

logger = logging.getLogger('django')


class Command(BaseCommand):
    args = '<feed_id>'
    help = "updates facebook_feed's is_current field"

    option_list = BaseCommand.option_list + (
        make_option('-m',
           '--set-value-manually',
           action='store',
           dest='set-value-manually',
           help='Set value of is_current field manually. Usage -m=True'),
    )

    def is_related_person_current(self, feed):
        if IS_ELECTIONS_MODE:
            return Candidate.objects.filter(pk=feed.persona.alt_object_id).exists()
        else:
            try:
                return Member.objects.get(pk=feed.persona.object_id).is_current
            except Member.DoesNotExist:
                return False


    def decide_is_current_field(self, feed, options):
        is_current_value = False

        manual_val = options['set-value-manually']
        if manual_val is not None:
            if manual_val.lower() == 'true':
                is_current_value = True
            elif manual_val.lower() == 'false':
                is_current_value = True
            else:
                warning_msg = 'manual input "%s" is incorrect, use True or False' % manual_val
                logger.warning(warning_msg)
                raise CommandError(warning_msg)

        else:
            # Feed unattached to mk is set to be non-current by default
            is_current_value = self.is_related_person_current(feed)

        print 'is_current_value for feed %s (#%s) is set to: %s' % (feed, feed.id, is_current_value)
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
