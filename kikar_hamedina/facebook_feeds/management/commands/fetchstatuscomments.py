import sys
from django.db.utils import IntegrityError
from time import sleep
import datetime
import dateutil
import logging
import urllib2
from optparse import make_option
from collections import defaultdict
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import facebook
from facebook import GraphAPIError
from facebook_feeds.models import Facebook_Status, User_Token, Facebook_Status_Attachment, Facebook_Status_Comment, \
    Facebook_User, Facebook_Status_Comment_Attachment

FACEBOOK_API_VERSION = getattr(settings, 'FACEBOOK_API_VERSION', 'v2.5')
NUMBER_OF_TRIES_FOR_REQUEST = 3
LENGTH_OF_EMPTY_ATTACHMENT_JSON = 21
DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN = 100
SLEEP_TIME = 3

# The error code from fb API for a deleted status.
DELETED_STATUS_ERROR_CODE = 100


class Command(BaseCommand):
    args = '<status_id>'
    help = 'Gets all comments for a given status'
    option_list = BaseCommand.option_list + (
        make_option('-f',
                    '--force-update',
                    action='store_true',
                    dest='force-update',
                    default=False,
                    help='Force update of status.'),
        make_option('-a',
                    '--force-attachment-update',
                    action='store_true',
                    dest='force-attachment-update',
                    default=False,
                    help='Use this flag to force updating of status attachment'),
        make_option('--from-date',
                    action='store',
                    type='string',
                    dest='from-date',
                    default=None,
                    help='Specify date from which to update the statuses (inclusive) e.g. 2014-03-31'),
        make_option('--to-date',
                    action='store',
                    type='string',
                    dest='to-date',
                    default=None,
                    help='Specify date until which to update the statuses (exclusive) e.g. 2014-03-31'),
        make_option('--feed-ids',
                    action='store',
                    type='string',
                    dest='feed-ids',
                    default=None,
                    help='Specify particular feed ids you want to update comments for with list of ids (e.g. 51, 54)'),
        make_option('--update-deleted',
                    action='store_true',
                    dest='update-deleted',
                    default=False,
                    help="Update is_deleted flag: set to True/False for deleted/existing statuses"),
    )

    graph = facebook.GraphAPI()

    def fetch_status_object_data(self, status_id, limit):
        """
        Receives a Facebook status ID
        Returns a dictionary with status properties, an empty dict on error or None if status believed to be deleted.
        :param limit:
        """
        print FACEBOOK_API_VERSION
        comments_number_limit = limit
        api_request_path = "{0}/comments/".format(status_id)
        args_for_request = {'version': FACEBOOK_API_VERSION,
                            'limit': comments_number_limit,
                            'fields': "from, message, id, created_time, attachment, like_count, comment_count, message_tags, comments",
                            'filter': 'toplevel',
                            'order': 'chronological'}

        try_number = 1
        while try_number <= NUMBER_OF_TRIES_FOR_REQUEST:
            num_of_pages = 1
            print 'page num: {}'.format(num_of_pages)
            try:
                return_statuses = self.graph.request(path=api_request_path, args=args_for_request)
            except Exception:
                warning_msg = "Failed an attempt for status #({0}) from FB API.".format(status_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                try_number += 1
                continue
            if not ('paging' in return_statuses and 'next' in return_statuses['paging']):
                print 'only one page, returning'
                return return_statuses

            print 'More than one page, trying to use paging'
            list_of_statuses = []
            list_of_statuses += return_statuses['data']
            args_for_request['after'] = return_statuses['paging']['cursors']['after']
            next_page = True
            while try_number <= NUMBER_OF_TRIES_FOR_REQUEST and next_page:
                num_of_pages += 1
                print 'page num: {}'.format(num_of_pages)
                try:
                    print args_for_request['after']
                    return_statuses = self.graph.request(path=api_request_path, args=args_for_request)
                except Exception:
                    warning_msg = "Failed an attempt for status #({0}) from FB API.".format(status_id)
                    logger = logging.getLogger('django')
                    logger.warning(warning_msg)
                    print 'try_number:', try_number
                    try_number += 1
                    continue
                list_of_statuses += return_statuses['data']
                if 'paging' in return_statuses and 'next' in return_statuses['paging']:
                    args_for_request['after'] = return_statuses['paging']['cursors']['after']
                else:
                    next_page = False

                if not num_of_pages % 5:
                    print 'sleeping for %d seconds.' % SLEEP_TIME
                    sleep(SLEEP_TIME)
            return_statuses = {'data': list_of_statuses}
            return return_statuses

    def get_picture_attachment_json(self, attachment):
        api_request_path = "{0}/".format(attachment.facebook_object_id)
        args_for_request = {'version': FACEBOOK_API_VERSION,
                            'fields': "id, images, height, source"}
        try_number = 1
        while try_number <= NUMBER_OF_TRIES_FOR_REQUEST:
            try:
                photo_object = self.graph.request(path=api_request_path, args=args_for_request)
                return photo_object
            except:
                warning_msg = "Failed first attempt for attachment #({0}) from FB API.".format(attachment.id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                try_number += 1
        error_msg = "Failed three attempts for feed #({0}) from FB API.".format(attachment.id)
        logger = logging.getLogger('django.request')
        logger.warning(error_msg)
        return {}

    def insert_comment_to_db(self, options, parent_status_object, retrieved_comment_data):
        """
        Receives a single status_object object as retrieved from facebook-sdk, and inserts the status_object
        to the db.
        """
        # Create a datetime object from int received in status_object

        comment_defaultdict = defaultdict(lambda: None, retrieved_comment_data)
        comment_id = comment_defaultdict['id']
        content = comment_defaultdict['message'] or ''
        like_count = comment_defaultdict['like_count'] or 0
        comment_count = comment_defaultdict['comment_count'] or 0
        message_tags = comment_defaultdict['message_tags']
        published = datetime.datetime.strptime(comment_defaultdict['created_time'],
                                               '%Y-%m-%dT%H:%M:%S+0000').replace(tzinfo=timezone.utc)
        try:
            comment_from_id = comment_defaultdict['from']['id']
            comment_from_name = comment_defaultdict['from']['name']
        except TypeError as e:
            comment_from_id = 1
            comment_from_name = 'Anonymous Facebook User'
        facebook_user, created = Facebook_User.objects.get_or_create(facebook_id=comment_from_id)
        if created:
            print '\tCreate Commentator'
            facebook_user.name = comment_from_name
            facebook_user.save()

        print '\tCreate comment_object'
        try:
            comment, created = Facebook_Status_Comment.objects.get_or_create(comment_id=comment_id,
                                                                             published=published,
                                                                             comment_from=facebook_user,
                                                                             parent=parent_status_object)

        except IntegrityError as e:
            print u'in Current Data: comment_id: {}, parent_id: {}, feed_id: {}\n text:{}'.format(comment_id,
                                                                                                  parent_status_object.status_id,
                                                                                                  parent_status_object.feed.id,
                                                                                                  content)
            db_comment = Facebook_Status_Comment.objects.get(comment_id=comment_id)
            print u'in DB: comment_id: {}, parent_id: {}, feed_id: {}\n text:{}'.format(db_comment.comment_id,
                                                                                        db_comment.parent.status_id,
                                                                                        db_comment.parent.feed.id,
                                                                                        db_comment.content)
            logger = logging.getLogger('django')
            logger.warning('integrity error at {}'.format(comment_id))
            return
        comment.parent = parent_status_object
        comment.comment_from = facebook_user
        comment.content = content
        comment.like_count = like_count
        comment.comment_count = comment_count
        comment.published = published
        comment.message_tags = message_tags
        comment.locally_updated = timezone.now()

        comment.save()
        if comment_defaultdict['attachment']:
            '\tSaving comment attachment'
            # Define:
            attachment_defaultdict = defaultdict(lambda: None, comment_defaultdict['attachment'])
            if attachment_defaultdict['media']:
                try:
                    comment_attachment_src = attachment_defaultdict['media']['image']['src']
                except TypeError as e:
                    print u'in Current Data: comment_id: {}, parent_id: {}, ' \
                          u'feed_id: {}\n text:{}'.format(comment_id,
                                                          parent_status_object.status_id,
                                                          parent_status_object.feed.id,
                                                          content)
                    print '{}'.format(attachment_defaultdict)
                    raise e
                comment_attachment_width = attachment_defaultdict['media']['image']['width']
                comment_attachment_height = attachment_defaultdict['media']['image']['height']
            else:
                comment_attachment_height = None
                comment_attachment_width = None
                comment_attachment_src = None
            comment_attachment_type = attachment_defaultdict['type']
            comment_attachment_name = attachment_defaultdict['title']
            comment_attachment_caption = attachment_defaultdict['caption']
            comment_attachment_description = attachment_defaultdict['description']
            comment_attachment_link = attachment_defaultdict['url']
            if attachment_defaultdict['type'] == 'avatar':
                comment_attachment_link = 'https://www.facebook.com/{}'.format(attachment_defaultdict['target']['id'])
            # Save:
            comment_attachment, created = Facebook_Status_Comment_Attachment.objects.get_or_create(comment=comment)
            comment_attachment.name = comment_attachment_name
            comment_attachment.caption = comment_attachment_caption
            comment_attachment.description = comment_attachment_description
            comment_attachment.link = comment_attachment_link
            comment_attachment.type = comment_attachment_type
            comment_attachment.source = comment_attachment_src
            comment_attachment.source_width = comment_attachment_width
            comment_attachment.source_height = comment_attachment_height
            comment_attachment.save()

    def set_deleted_status_in_db(self, status):
        """Set is_deleted flag to True and save status"""
        status.is_deleted = True
        status.save()

    def fetch_comments_data(self, status, limit):
        """
        Returns a Dict object with Status data, by Status ID, empty Dict if not working,
        None if status deleted.
        :param limit:
        """

        status_dict = dict()
        is_skip = False
        if status.feed.feed_type == 'PP':
            try:
                # Set facebook graph access token to most up-to-date user token in db
                token = User_Token.objects.first()
                self.graph.access_token = token.token

            except AttributeError:
                # exception - trying to set an empty token (NoneType) as graph.access_token
                # Fallback: Set facebook graph access token to app access token
                self.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                        settings.FACEBOOK_SECRET_KEY)
                if status.feed.requires_user_token:
                    # If the Status's Feed is set to require a user-token, and none exist in our db, the feed is skipped.
                    print 'feed %d requires user token, skipping.' % status.id
                    is_skip = True

                    # Get the data using the pre-set token

        elif status.feed.feed_type == 'UP':  # feed_type == 'UP' - User Profile
            # Set facebook graph access token to user access token
            token = User_Token.objects.filter(feeds__id=status.id).order_by('-date_of_creation').first()
            if not token:
                print 'No Token found for User Profile %s' % status
                is_skip = True
            else:
                print 'using token by user_id: %s' % token.user_id
                self.graph.access_token = token.token

        else:  # Deprecated or malfunctioning profile ('NA', 'DP')
            print 'Profile %s is of type %s, skipping.' % (status.id, status.feed_type)
            is_skip = True

        if not is_skip:
            status_dict = self.fetch_status_object_data(status.status_id, limit)
        return status_dict

    def handle(self, *args, **options):
        """
        Executes fetchstatuscomments manage.py command.
        Receives either one status ID and updates the data for that status,
        or no status ID and therefore retrieves all Statuses and updates their data one by one.

        Options exist for running within a given date range.
        """

        post_number_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN
        print 'Variable post_number_limit set to: {0}.'.format(post_number_limit)

        list_of_statuses = list()
        # Case no args - fetch all statuses or by options
        if len(args) == 0:
            criteria = {}
            if options['from-date']:
                criteria['published__gte'] = dateutil.parser.parse(options['from-date'])
            if options['to-date']:
                criteria['published__lt'] = dateutil.parser.parse(options['to-date'])
            if options['feed-ids']:
                criteria['feed__id__in'] = options['feed-ids'].split(',')
            db_statuses = Facebook_Status.objects_no_filters.filter(**criteria).order_by('-published')
            list_of_statuses = list(db_statuses)

        # Case arg exists - fetch status by id supplied
        elif len(args) == 1:
            status_id = args[0]
            try:
                status = Facebook_Status.objects_no_filters.get(status_id=status_id)
                list_of_statuses.append(status)

            except Facebook_Status.DoesNotExist:
                warning_msg = "Status #({0}) does not exist.".format(status_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                raise CommandError('Status "%s" does not exist' % status_id)

        # Case invalid args
        else:
            raise CommandError('Please enter a valid status id')

        self.stdout.write('Starting to update {0} statuses'.format(len(list_of_statuses)))

        # Iterate over list_of_statuses
        for i, status in enumerate(list_of_statuses):
            self.stdout.write(
                'Working on status {0} of {1}: {2}.'.format(i + 1, len(list_of_statuses), status.status_id))
            comments_data = self.fetch_comments_data(status=status, limit=post_number_limit)
            self.stdout.write('Successfully fetched comments for: {0}.'.format(status.status_id))

            if comments_data:
                for comment_data in comments_data['data']:
                    self.insert_comment_to_db(options=options, parent_status_object=status,
                                              retrieved_comment_data=comment_data)
                self.stdout.write(
                    'Successfully written {} comments for status: {}.'.format(len(comments_data['data']),
                                                                              status.status_id))
                info_msg = "Successfully updated comments for status: {0}.\t {1}".format(status.status_id,
                                                                                         status.published)

            elif comments_data is None:  # Status deleted
                if options['update-deleted']:
                    self.set_deleted_status_in_db(status)
                    info_msg = 'Successfully marked status deleted: {0}.'.format(status.pk)
                    self.stdout.write(info_msg)
                else:
                    self.stdout.write(
                        'Ignoring deleted status: {0} (use --update-deleted to update DB).'.format(status.pk))
                    info_msg = 'Ignoring deleted status: {0}.'.format(status.pk)

            else:
                self.stdout.write('No data was retrieved for status: {0}.'.format(status.id))
                info_msg = "Did not successfully update status: {0}.".format(status.pk)

            logger = logging.getLogger('django')
            logger.info(info_msg)

        info_msg = "Successfully saved all statuses to db"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully saved all statuses to db.')
