import datetime
from pprint import pprint
from optparse import make_option
from collections import defaultdict
from unidecode import unidecode

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.core.mail import send_mail
import facebook
import logging
from ...models import \
    Facebook_Feed as Facebook_Feed_Model, \
    Facebook_Status as Facebook_Status_Model, \
    User_Token as User_Token_Model, \
    Facebook_Status_Attachment as Facebook_Status_Attachment_Model

FACEBOOK_API_VERSION = getattr(settings, 'FACEBOOK_API_VERSION', 'v2.1')

NUMBER_OF_TRIES_FOR_REQUEST = 3

LENGTH_OF_EMPTY_ATTACHMENT_JSON = 21

DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN = 100
DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN = 20


class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Fetches a feed'
    option_list = BaseCommand.option_list + (
        make_option('-i',
                    '--initial',
                    action='store_true',
                    dest='initial',
                    default=False,
                    help='Flag initial runs fql query with limit of {0} instead of regular limit of {1}.'
                    .format(DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN,
                            DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN)),
        make_option('-f',
                    '--force-update',
                    action='store_true',
                    dest='force-update',
                    default=False,
                    help='Use this flag to force updating of status/'),
        make_option('-a',
                    '--force-attachment-update',
                    action='store_true',
                    dest='force-attachment-update',
                    default=False,
                    help='Use this flag to force updating of status attachment'),
        make_option('-t',
                    '--request-timeout',
                    dest='request-timeout',
                    type='int',
                    default=20,
                    help='Timeout for Facebook API requests in seconds'),
        make_option('-c',
                    '--current-only',
                    action='store_true',
                    dest='current-only',
                    default=False,
                    help='Whether to update only feeds of current members (false means all members)'),
    )

    def fetch_status_objects_from_feed(self, feed_id, post_number_limit):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
                """
        api_request_path = "{0}/posts".format(feed_id)
        args_for_request = {'limit': post_number_limit,
                            'version': FACEBOOK_API_VERSION,
                            'fields': "from, message, id, created_time, \
                             updated_time, type, link, caption, picture, full_picture, description, name,\
                             status_type, story, story_tags ,object_id, properties, source, to, shares, \
                             likes.summary(true).limit(1), comments.summary(true).limit(1)"}

        try_number = 1
        while try_number <= NUMBER_OF_TRIES_FOR_REQUEST:
            try:
                return_statuses = self.graph.request(path=api_request_path, args=args_for_request)
                return return_statuses
            except Exception:
                warning_msg = "Failed first attempt for feed #({0}) from FB API.".format(feed_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                try_number += 1
        error_msg = "Failed three attempts for feed #({0}) from FB API.".format(feed_id)
        logger = logging.getLogger('django.request')
        logger.warning(error_msg)
        return []

    def get_picture_attachment_json(self, attachment):
        api_request_path = "{0}/".format(attachment.facebook_object_id)
        args_for_request = {'version': FACEBOOK_API_VERSION,
                            'fields': "id, images, height, source"}
        try_number = 1
        while try_number <= NUMBER_OF_TRIES_FOR_REQUEST:
            try:
                photo_object = self.graph.request(path=api_request_path, args=args_for_request)
                return photo_object
            except Exception:
                warning_msg = "Failed first attempt for attachment #({0}) from FB API.".format(attachment.id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                try_number += 1
        error_msg = "Failed three attempts for feed #({0}) from FB API.".format(attachment.id)
        logger = logging.getLogger('django.request')
        logger.warning(error_msg)
        return {}


    @staticmethod
    def insert_status_attachment(status, status_object_defaultdict):
        # print 'insert attachment'
        attachment_defaultdict = defaultdict(str, status_object_defaultdict)
        attachment = Facebook_Status_Attachment_Model(
            status=status,
            name=attachment_defaultdict['name'],
            caption=attachment_defaultdict['caption'],
            description=attachment_defaultdict['description'],
            link=attachment_defaultdict['link'],
            facebook_object_id=attachment_defaultdict['object_id'],
            type=attachment_defaultdict['type'],
            picture=attachment_defaultdict['picture']
        )
        attachment.save()
        # add all media files related to attachment

    def update_status_attachment(self, attachment, status_object_defaultdict):
        # print 'update attachment'
        attachment_defaultdict = defaultdict(str, status_object_defaultdict)
        if attachment_defaultdict['link']:
            # Update relevant attachment fields
            attachment.name = attachment_defaultdict['name']
            attachment.caption = attachment_defaultdict['caption']
            attachment.description = attachment_defaultdict['description']
            attachment.link = attachment_defaultdict['link']
            attachment.facebook_object_id = attachment_defaultdict['object_id']
            attachment.type = attachment_defaultdict['type']
            attachment.picture = attachment_defaultdict['picture']
            # get source for picture attachments
            if attachment.type == 'photo':
                print '\tgetting picture source'
                photo_object = self.get_picture_attachment_json(attachment)
                selected_attachment_object = sorted(photo_object['images'], key=lambda x: x['height'], reverse=True)[0]
                attachment.source = selected_attachment_object['source']
                attachment.source_width = selected_attachment_object['width']
                attachment.source_height = selected_attachment_object['height']
            elif attachment.type == 'video':
                print '\tsetting video source'
                attachment.source = attachment_defaultdict['source']
            elif attachment.type == 'link':
                print '\tsetting link source'
                attachment.source = attachment_defaultdict['full_picture']
            attachment.save()
        else:
            # if has no link field - then there's no attachment, and it must be deleted
            # print 'deleting attachment'
            attachment.delete()

    def create_or_update_attachment(self, status, status_object_defaultdict):
        """
        If attachment exists, create or update all relevant fields.
        """
        # print 'create_or_update attachment'
        if status_object_defaultdict['link']:
            attachment, created = Facebook_Status_Attachment_Model.objects.get_or_create(
                status=status)
            # print 'I have an attachment. Created now: %s; Length of data in field link: %d; field picture: %d;  id: %s' % (
            # created, len(status_object_defaultdict['link']), len(str(status_object_defaultdict['picture'])),
            # status.status_id)
            self.update_status_attachment(attachment, status_object_defaultdict)
        else:
            pass
            # print 'i don''t have an attachment; Link field: %s; Picture field: %s; id: %s' % (
            # str(status_object_defaultdict['link']), str(status_object_defaultdict['picture']), status.status_id)

    def insert_status_object_to_db(self, status_object, feed_id, options):
        """
        Receives a single status object as retrieved from facebook-sdk, an inserts the status
        to the db.
                """
        # Create a datetime object from int received in status_object
        current_time_of_update = datetime.datetime.strptime(status_object['updated_time'],
                                                            '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=timezone.utc)

        def_dict_rec = lambda: defaultdict(def_dict_rec)

        status_object_defaultdict = defaultdict(lambda: None, status_object)
        if status_object_defaultdict['message']:
            message = status_object_defaultdict['message']
        else:
            message = ''
        if status_object_defaultdict['likes']:
            like_count = status_object_defaultdict['likes']['summary']['total_count']
        else:
            like_count = 0
        if status_object_defaultdict['comments']:
            comment_count = status_object_defaultdict['comments']['summary']['total_count']
        else:
            comment_count = 0
        if status_object_defaultdict['shares']:
            share_count = status_object_defaultdict['shares']['count']
        else:
            share_count = 0
        if status_object_defaultdict['status_type']:
            type_of_status = status_object_defaultdict['status_type']
        else:
            type_of_status = None
        if status_object_defaultdict['story']:
            story = status_object_defaultdict['story']
        else:
            story = None
        if status_object_defaultdict['story_tags']:
            story_tags = status_object_defaultdict['story_tags']
        else:
            story_tags = None

        published = datetime.datetime.strptime(status_object_defaultdict['created_time'],
                                               '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=timezone.utc)

        try:
            # If post_id already exists in DB
            status = Facebook_Status_Model.objects_no_filters.get(
                status_id=status_object['id'])  # use objects_default manages to get statuses that are comments as well.

            if status.updated < current_time_of_update or options['force-update']:
                # If post_id exists but of earlier update time, fields are updated.
                print 'update status'
                status.content = message
                status.like_count = like_count
                status.comment_count = comment_count
                status.share_count = share_count
                status.status_type = type_of_status  # note that fb has type AND status_type fields, here is status_type
                status.updated = current_time_of_update
                status.story = story
                status.story_tags = story_tags
                status.is_comment = status.set_is_comment

                status.save()

                # update attachment data
                self.create_or_update_attachment(status, status_object_defaultdict)
            elif options['force-attachment-update']:
                # force update of attachment, regardless of time
                status.save()
                self.create_or_update_attachment(status, status_object_defaultdict)
                # If post_id exists but of equal or later time (unlikely, but may happen), disregard
                # Should be an else here for this case but as it is, just disregard
        except Facebook_Status_Model.DoesNotExist:
            # If post_id does not exist at all, create it from data.
            print 'create status'
            status = Facebook_Status_Model(feed_id=feed_id,
                                           status_id=status_object['id'],
                                           content=message,
                                           like_count=like_count,
                                           comment_count=comment_count,
                                           share_count=share_count,
                                           published=published,
                                           updated=current_time_of_update,
                                           status_type=type_of_status,
                                           story=story,
                                           story_tags=story_tags)

            status.is_comment = status.set_is_comment

            if status_object_defaultdict['link']:
                # There's an attachment
                status.save()
                self.insert_status_attachment(status, status_object_defaultdict)
        finally:
            # save status object.
            print 'saving status'
            status.save()

    def get_feed_statuses(self, feed, post_number_limit):
        """
        Returns a Dict object of feed ID. and retrieved status objects.
        """
        if feed.feed_type == 'PP':
            try:
                # Set facebook graph access token to most up-to-date user token in db
                token = User_Token_Model.objects.first()
                self.graph.access_token = token.token

            except AttributeError:
                # Fallback: Set facebook graph access token to app access token
                self.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                        settings.FACEBOOK_SECRET_KEY)
                if feed.requires_user_token:
                    # If the Feed is set to require a user-token, and none exist in our db, the feed is skipped.
                    print 'feed %d requires user token, skipping.' % feed.id
                    data_dict = {'feed_id': feed.id, 'statuses': []}
                    return data_dict

                    # Get the data using the pre-set token
            return {'feed_id': feed.id,
                    'statuses': self.fetch_status_objects_from_feed(feed.vendor_id, post_number_limit)}

        elif feed.feed_type == 'UP':  # feed_type == 'UP' - User Profile
            # Set facebook graph access token to user access token
            token = User_Token_Model.objects.filter(feeds__id=feed.id).order_by('-date_of_creation').first()
            if not token:
                print 'No Token found for User Profile %s' % feed
                return {'feed_id': feed.id, 'statuses': []}
            else:
                print 'using token by user_id: %s' % token.user_id
                self.graph.access_token = token.token
                return {'feed_id': feed.id,
                        'statuses': self.fetch_status_objects_from_feed(feed.vendor_id, post_number_limit)}
        else:  # Deprecated or malfunctioning profile ('NA', 'DP')
            print 'Profile %s is of type %s, skipping.' % (feed.id, feed.feed_type)
            return {'feed_id': feed.id, 'statuses': []}

    def handle(self, *args, **options):
        """
        Executes fetchfeed manage.py command.
        Receives either one feed ID and retrieves Statuses for that feed,
        or no feed ID and therefore retrieves all Statuses for all the feeds.
        """
        self.graph = facebook.GraphAPI(timeout=options['request-timeout'])

        feeds_statuses = []
        if options['initial']:
            post_number_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN
        else:
            post_number_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN
        print 'Variable post_number_limit set to: {0}.'.format(post_number_limit)

        list_of_feeds = list()
        # Case no args - fetch all feeds
        if len(args) == 0:
            manager = Facebook_Feed_Model.current_feeds if options['current-only'] else Facebook_Feed_Model.objects
            list_of_feeds = [feed for feed in manager.all()]
        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])
            try:
                feed = Facebook_Feed_Model.objects.get(pk=feed_id)
                list_of_feeds.append(feed)
            except Facebook_Feed_Model.DoesNotExist:
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
            feed_statuses = self.get_feed_statuses(feed, post_number_limit)
            self.stdout.write('Successfully fetched feed: {0}.'.format(feed.pk))
            if feed_statuses['statuses']:
                for status in feed_statuses['statuses']['data']:
                    self.insert_status_object_to_db(status, feed_statuses['feed_id'], options)
                self.stdout.write('Successfully written feed: {0}.'.format(feed.pk))
            else:
                self.stdout.write('No statuses retrieved for feed: {0}, {1}.'.format(feed.id, feed.vendor_id))
            info_msg = "Successfully updated feed: {0}.".format(feed.pk)
            logger = logging.getLogger('django')
            logger.info(info_msg)
        info_msg = "Successfully saved all statuses to db"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully saved all statuses to db.')
