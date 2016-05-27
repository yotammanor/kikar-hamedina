import json
import urllib
from csv import DictReader

from time import sleep
import dateutil
import logging
from optparse import make_option
from collections import defaultdict
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
import facebook
from facebook_feeds.models import Facebook_Status, User_Token, Facebook_User, Facebook_Like

FACEBOOK_API_VERSION = getattr(settings, 'FACEBOOK_API_VERSION', 'v2.5')
NUMBER_OF_TRIES_FOR_REQUEST = getattr(settings, 'NUMBER_OF_TRIES_FOR_REQUEST', 2)
LENGTH_OF_EMPTY_ATTACHMENT_JSON = 21
DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN = 100
SLEEP_TIME = 3

# The error code from fb API for a deleted status.
DELETED_STATUS_ERROR_CODE = 100


class Command(BaseCommand):
    args = '<status_id>'
    help = 'Gets all Likes for a given status.'
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
                    help='Specify particular feed ids you want to update likes for with list of ids (e.g. 51, 54)'),
        make_option('--update-deleted',
                    action='store_true',
                    dest='update-deleted',
                    default=False,
                    help="Update is_deleted flag: set to True/False for deleted/existing statuses"),
        make_option('--file',
                    action='store',
                    dest='file_path',
                    default=None,
                    help="execute on list of status ids from file"),
    )

    graph = facebook.GraphAPI()

    def fetch_status_object_data(self, status_id, limit):
        """
        Receives a Facebook status ID
        Returns a dictionary with status properties, an empty dict on error or None if status believed to be deleted.
        :param limit: num of elements (status likes) per response
        :param status_id: likes for this status

        """
        api_version = 'v2.6'
        likes_number = limit
        api_request_path = "{0}/{1}/reactions/".format(api_version, status_id)
        args_for_request = {'limit': likes_number,
                            'fields': "id,username,link,name,type,profile_type",
                            }

        try_number = 1
        while try_number <= NUMBER_OF_TRIES_FOR_REQUEST:
            num_of_pages = 1
            print('page num: {}'.format(num_of_pages))

            try:
                return_statuses = self.graph.request(path=api_request_path, args=args_for_request)
            except Exception as e:
                warning_msg = "Failed an attempt for status #({0}) from FB API.".format(status_id)
                print(e)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                try_number += 1
                continue
            if not ('paging' in return_statuses and 'next' in return_statuses['paging']):
                print('only one page, returning')
                return return_statuses

            print('More than one page, trying to use paging')
            list_of_statuses = []
            list_of_statuses += return_statuses['data']
            args_for_request['after'] = return_statuses['paging']['cursors']['after']
            next_page = True
            while try_number <= NUMBER_OF_TRIES_FOR_REQUEST and next_page:
                num_of_pages += 1
                print('page num: {}'.format(num_of_pages))
                try:
                    print(args_for_request['after'])
                    return_statuses = self.graph.request(path=api_request_path, args=args_for_request)
                except Exception:
                    warning_msg = "Failed an attempt for status #({0}) from FB API.".format(status_id)
                    logger = logging.getLogger('django')
                    logger.warning(warning_msg)
                    print('try_number:', try_number)
                    try_number += 1
                    continue
                list_of_statuses += return_statuses['data']
                if 'paging' in return_statuses and 'next' in return_statuses['paging']:
                    args_for_request['after'] = return_statuses['paging']['cursors']['after']
                else:
                    next_page = False

                if not num_of_pages % 5:
                    print('sleeping for %d seconds.' % SLEEP_TIME)
                    sleep(SLEEP_TIME)
            return_statuses = {'data': list_of_statuses}
            return return_statuses

    def insert_like_to_db(self, options, parent_status_object, retrieved_like_data):
        """
        Receives a single like data instance as retrieved from facebook-sdk, and inserts the data to
        the db.
        """

        like_defaultdict = defaultdict(lambda: None, retrieved_like_data)
        like_type = like_defaultdict['type'] or ''
        like_type = like_type.lower()
        try:
            like_from_id = like_defaultdict['id']
            like_from_name = like_defaultdict['name']
        except TypeError as e:
            like_from_id = 1
            like_from_name = 'Anonymous Facebook User'

        facebook_user, created = Facebook_User.objects.get_or_create(facebook_id=like_from_id)
        if created:
            print('\tCreate Liking User')
            facebook_user.name = like_from_name
        facebook_user.type = like_defaultdict['profile_type']
        facebook_user.save()

        print('\tCreate like_object')

        like_obj, created = Facebook_Like.objects.get_or_create(status=parent_status_object, user=facebook_user)
        like_obj.type = like_type
        like_obj.save()

    def set_deleted_status_in_db(self, status):
        """Set is_deleted flag to True and save status"""
        status.is_deleted = True
        status.save()

    def fetch_likes_data(self, status, limit):
        """
        Returns a Dict object with Status likes data, by Status ID, empty Dict if not working,
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
                    print('feed %d requires user token, skipping.' % status.id)
                    is_skip = True

                    # Get the data using the pre-set token

        elif status.feed.feed_type == 'UP':  # feed_type == 'UP' - User Profile
            # Set facebook graph access token to user access token
            token = User_Token.objects.filter(feeds__id=status.id).order_by('-date_of_creation').first()
            if not token:
                print('No Token found for User Profile %s' % status)
                is_skip = True
            else:
                print('using token by user_id: %s' % token.user_id)
                self.graph.access_token = token.token

        else:  # Deprecated or malfunctioning profile ('NA', 'DP')
            print('Profile %s is of type %s, skipping.' % (status.id, status.feed_type))
            is_skip = True

        if not is_skip:
            status_dict = self.fetch_status_object_data(status.status_id, limit)
        return status_dict

    def handle(self, *args, **options):
        """
        Executes fetchstatuslikes manage.py command.
        Receives either one status ID or filtering options for multiple statuses,
        and updates the likes data for status(es) selected.

        Options exist for running within a given date range.
        """

        post_number_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN
        print('Variable post_number_limit set to: {0}.'.format(post_number_limit))

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

            if options['file_path']:
                with open(options['file_path'], 'r') as f:
                    reader = DictReader(f)
                    list_of_statuses = [x['status_id'] for x in reader]

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
            likes_data = self.fetch_likes_data(status=status, limit=post_number_limit)
            self.stdout.write('Successfully fetched likes for: {0}.'.format(status.status_id))

            if likes_data:
                for like_data in likes_data['data']:
                    self.insert_like_to_db(options=options, parent_status_object=status,
                                           retrieved_like_data=like_data)
                self.stdout.write(
                    'Successfully written {} likes for status: {}.'.format(len(likes_data['data']),
                                                                           status.status_id))
                info_msg = "Successfully updated likes for status: {0}.\t {1}".format(status.status_id,
                                                                                      status.published)

            elif likes_data is None:  # Status deleted
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
