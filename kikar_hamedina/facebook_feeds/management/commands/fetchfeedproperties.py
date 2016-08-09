import datetime
import sys
from optparse import make_option
from collections import defaultdict
from pprint import pprint
import logging
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
import facebook
from unidecode import unidecode

from core.models import MEMBER_MODEL
from facebook_feeds.models import \
    Facebook_Feed, \
    Facebook_Status, \
    User_Token, \
    Feed_Popularity
from concurrent import futures

FACEBOOK_API_VERSION = getattr(settings, 'FACEBOOK_API_VERSION', 'v2.7')
_LOGGER_SCRAPING = logging.getLogger('scraping')


# Todo: using single transaction (?)
class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Fetches feed properties from Facebook API and updates to DB.'
    errors_count = 0
    warning_count = 0

    option_insist = make_option('-n',
                                '--insist',
                                action='store_true',
                                dest='is_insist',
                                default=False,
                                help='Exception from GraphAPI will result in skipping instead of crashing.'
                                )

    option_app_token = make_option('-t',
                                   '--use-app-token',
                                   action='store_true',
                                   dest='use_app_token',
                                   default=False,
                                   help='Use app access token for all types and cases of requests'
                                   )

    option_mk_id = make_option('-m',
                               '--mk',
                               action='store',
                               dest='mk_id',
                               default=None,
                               help='Update Main feed that belongs to MK id'
                               )

    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list_helper.append(option_insist)
    option_list_helper.append(option_app_token)
    option_list_helper.append(option_mk_id)
    option_list = tuple(option_list_helper)

    graph = facebook.GraphAPI()

    def fetch_data_by_feed_id(self, feed_id, fetch_fields, is_insist):
        """
        Receives a feed_id for a facebook
        Returns properties about this feed
        """
        api_request_path = "{0}/{1}".format(FACEBOOK_API_VERSION, str(feed_id))

        args_for_request = {
            'fields': fetch_fields
        }

        try:
            user_profile_properties = self.graph.request(path=api_request_path, args=args_for_request)
        except facebook.GraphAPIError as e:
            self.errors_count = + 1
            _LOGGER_SCRAPING.warning('Fetch Feed Properties: GraphAPI error, feed #%s. %s: %s',
                                     feed_id,
                                     'processing anyway...' if is_insist else 'process aborted.',
                                     e)
            if is_insist:
                user_profile_properties = {}
            else:
                raise

        try:
            user_profile_properties['picture_large'] = user_profile_properties['picture']['data']['url']
        except (LookupError, TypeError):
            self.warning_count = + 1
            # Fallback: assign null value to picture_large
            user_profile_properties['picture_large'] = None
            _LOGGER_SCRAPING.warning('Fetch Feed Properties: feed #{0} has no large pic'
                                     .format(feed_id))

        return user_profile_properties

    def update_feed_data_to_db(self, feed_data, feed_pk_id):
        """
        Receives a single Facebook_Page data object as retrieved from facebook-sdk,
        and updates the data into Facebook_Feed in the db.
        """
        try:
            if feed_data:
                feed_dict = defaultdict(str, feed_data)
                # If post_id already exists in DB
                feed = Facebook_Feed.objects.get(id=feed_pk_id)
                # Assuming retrieved data from facebook is always more up-to-date than our data
                feed.about = feed_dict['about']
                feed.birthday = feed_dict['birthday']
                feed.name = feed_dict['name']
                feed.link = feed_dict['link']
                feed.picture_square = feed_dict['picture']['data']['url']
                feed.picture_large = feed_dict['picture_large']
                feed.username = feed_dict['username']
                feed.website = feed_dict['website']
                feed.current_fan_count = feed_dict['fan_count']
                # save feed object.
                feed.save()
                # feed_popularity data
                feed_popularity = Feed_Popularity(
                    feed=feed,
                    date_of_creation=timezone.now(),
                    fan_count=feed_dict['fan_count'],
                    talking_about_count=feed_dict['talking_about_count'],
                )
                feed_popularity.save()
            else:
                self.warning_count += 1
                _LOGGER_SCRAPING.warning('Fetch Feed Properties: Feed pk #{0} no data retrieved for feed'
                                         .format(feed_pk_id))
        except Facebook_Feed.DoesNotExist:
            self.errors_count += 1
            _LOGGER_SCRAPING.error('Fetch Feed Properties: Feed pk #{0} is missing from db'
                                   .format(feed_pk_id))
            raise

    def get_feed_data(self, feed, is_insist, use_app_token):
        """
        Returns a Dict object of feed ID. and retrieved feed data.
        :param use_app_token:
        """
        empty_data_dict = {'feed_id': feed.id, 'data': {}}

        if feed.feed_type == 'UP':  # User Profile
            # Set facebook graph access token to user access token
            token = None

            if not feed.requires_user_token:
                token = feed.tokens.order_by('-date_of_creation').first()
            else:
                # feed does not require a particular user token
                token = User_Token.objects.order_by('-date_of_creation').first()

            # first() returns the first row or None if not found.
            if token:
                self.graph.access_token = token.token
            else:
                self.warning_count += 1
                _LOGGER_SCRAPING.warning('Fetch Feed Properties: UP Feed pk #{0} requires user token but not found one'
                                         .format(feed.id))
                return empty_data_dict

            data_dict = {'feed_id': feed.id, 'data':
                self.fetch_data_by_feed_id(feed.vendor_id,
                                           "id,name,picture.type(large).fields(url),website,about,link,first_name,last_name,birthday",
                                           is_insist)}

            # Transform data to fit existing public page
            data_dict['data']['username'] = ''.join(
                (data_dict['data']['first_name'], data_dict['data']['last_name'])).lower()
            data_dict['data']['likes'] = 0
            data_dict['data']['talking_about_count'] = 0
            data_dict['data']['about'] = None
            return data_dict

        elif feed.feed_type == 'PP':  # 'PP - Public Page'
            try:
                # Set facebook graph access token to most up-to-date user token in db
                token = User_Token.objects.order_by('-date_of_creation').first()
                self.graph.access_token = token.token
            except Exception as e:
                if feed.requires_user_token:
                    self.warning_count += 1
                    # If the Feed is set to require a user-token, and none exist in our db, the feed is skipped.
                    _LOGGER_SCRAPING.warning(
                        'Fetch Feed Properties: PP Feed pk #{0} requires user token but not found one'
                            .format(feed.id))
                    return empty_data_dict

                # Fallback: Set facebook graph access token to app access token
                self.graph.access_token = self.graph.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                          settings.FACEBOOK_SECRET_KEY)
        else:  # Deprecated or malfunctioning profile ('NA', 'DP')
            _LOGGER_SCRAPING.info('Fetch Feed Properties: Feed pk {0} is of type {1}, skipping.'
                                  .format(feed.id, feed.feed_type))
            return empty_data_dict

        if use_app_token and not feed.requires_user_token:
            self.graph.access_token = self.graph.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                      settings.FACEBOOK_SECRET_KEY)
        # Get the data using the pre-set token
        data_dict = {'feed_id': feed.id, 'data':
            self.fetch_data_by_feed_id(feed.vendor_id,
                                       "id,name,username,picture.type(large).fields(url),about,birthday,website,link,fan_count,talking_about_count",
                                       is_insist)}
        return data_dict

    def handle(self, *args, **options):
        """
        Executes fetchfeedproperties manage.py command.
        Receives either one feed ID and retrieves the relevant page's data, and updates them in the db,
        or no feed ID and therefore retrieves data for all the feeds.
        """
        is_insist = options['is_insist']
        use_app_token = options['use_app_token']
        list_of_feeds = list()

        if options['mk_id']:
            try:
                feed = MEMBER_MODEL.objects.get(id=options['mk_id']).facebook_persona.get_main_feed
                list_of_feeds.append(feed)
            except (Facebook_Feed.DoesNotExist, MEMBER_MODEL.DoesNotExist) as e:
                raise CommandError('No Feed found for MK ID:{}'.format(options['mk_id']))

        # Case no args - fetch all feeds
        elif len(args) == 0:
            list_of_feeds = [feed for feed in Facebook_Feed.objects.all().filter(feed_type='PP')]
        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_pk_id = int(args[0])
            try:
                feed = Facebook_Feed.objects.get(pk=feed_pk_id)
                list_of_feeds.append(feed)
            except Facebook_Feed.DoesNotExist:
                self.warning_count += 1
                _LOGGER_SCRAPING.warning('Fetch Feed Properties: Feed pk #{0} is missing from db'
                                         .format(feed_pk_id))
                raise CommandError('Feed "%s" does not exist' % feed_pk_id)
        else:
            raise CommandError('Please enter a valid feed id')

        def worker(feed):
            self.stdout.write('Working on feed: {0} (Member ID:{1}).'.format(feed.pk, feed.persona.object_id))
            # get feed properties from facebook
            feed_data = self.get_feed_data(feed, is_insist, use_app_token)
            # update fetched data to feed in database
            if feed_data['data']:
                self.update_feed_data_to_db(feed_data['data'], feed_data['feed_id'])

        # Actually do work!
        with futures.ThreadPoolExecutor(max_workers=10) as executer:
            [executer.submit(worker, feed) for feed in list_of_feeds]

        self.stdout.write('Done. warnings: {0}, errors: {1}. See the log file for more details.'.format(
            self.warning_count, self.errors_count
        ))
