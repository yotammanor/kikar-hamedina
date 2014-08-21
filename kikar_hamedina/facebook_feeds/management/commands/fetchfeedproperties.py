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
from ...models import \
    Facebook_Feed as Facebook_Feed_Model, \
    Facebook_Status as Facebook_Status_Model, \
    User_Token as User_Token_Model, \
    Feed_Popularity as Feed_Popularity_Model

FACEBOOK_API_VERSION = 'v2.0'


class Command(BaseCommand):
    args = '<person_id>'
    help = 'Fetches a person'

    option_insist = make_option('-n',
                                '--insist',
                                action='store_true',
                                dest='is_insist',
                                default=False,
                                help='Exception from GraphAPI will result in skipping instead of crashing.'
    )

    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list_helper.append(option_insist)
    option_list = tuple(option_list_helper)

    graph = facebook.GraphAPI()

    def fetch_user_profile_object_by_feed_id(self, feed_id, is_insist):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
                """
        api_request = "{0}".format(feed_id)
        args_for_request = {'version': FACEBOOK_API_VERSION,
                            'fields': "id,name,picture.type(square).fields(url),website,about,link,first_name,last_name,birthday"}


        args_for_large_pic_request = {'version': FACEBOOK_API_VERSION,
                                      'fields': 'picture.type(large).fields(url)'}
        # '508516607','107836625941364'

        try:
            user_profile_properties = self.graph.request(path=api_request, args=args_for_request)
            large_pic_response = self.graph.request(path=api_request, args=args_for_large_pic_request)
        except facebook.GraphAPIError:
            if is_insist:
                print "There's a GraphAPI error, but I'm going on anyway."
                # TODO: Log and report by email!
                user_profile_properties = {}
                large_pic_response = {'picture': {'data': {'url': ''}}}

            else:
                print "Your circuit's dead there's something wrong!"
                raise
        try:
            user_profile_properties['pic_large'] = large_pic_response['picture']['data']['url']
        except KeyError:
            print 'problem with large_pic_response_dict'
            sys.exc_info()
        return user_profile_properties

    def fetch_public_page_object_by_feed_id(self, feed_id, is_insist):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
                """

        api_request = "{0}".format(feed_id)
        args_for_request = {'version': FACEBOOK_API_VERSION,
                            'fields': "id,name,username,picture.type(square).fields(url),about,birthday,website,link,likes,talking_about_count"}

        args_for_large_pic_request = {'version': FACEBOOK_API_VERSION,
                                      'fields': 'picture.type(large).fields(url)'}

        print api_request, args_for_request
        try:
            public_page_properties = self.graph.request(path=api_request, args=args_for_request)
            large_pic_response = self.graph.request(path=api_request, args=args_for_large_pic_request)
        except facebook.GraphAPIError:
            if is_insist:
                print "There's a GraphAPI error, but I'm going on anyway."
                # TODO: Log and report by email!
                public_page_properties = {}
                large_pic_response = {'picture': {'data': {'url': ''}}}
            else:
                print "Your circuit's dead there's something wrong!"
                raise
        try:
            public_page_properties['pic_large'] = large_pic_response['picture']['data']['url']
        except KeyError:
            print 'problem with large_pic_response_dict'
            sys.exc_info()
        print public_page_properties
        return public_page_properties


    def update_feed_data_to_db(self, feed_data, feed_id):
        """
        Receives a single Facebook_Page data object as retrieved from facebook-sdk,
        and updates the data into Facebook_Feed in the db.
                """
        # Create a datetime object from int received in status_object
        # current_time_of_update = datetime.datetime.fromtimestamp(feed_data['updated_time'],tz=timezone.utc)
        try:
            if feed_data:
                feed_dict = defaultdict(str, feed_data)
                # If post_id already exists in DB
                feed = Facebook_Feed_Model.objects.get(id=feed_id)
                # Assuming retrieved data from facebook is always more up-to-date than our data
                feed.about = feed_dict['about']
                feed.birthday = feed_dict['birthday']
                feed.name = feed_dict['name']
                feed.link = feed_dict['link']
                feed.picture_square = feed_dict['picture']['data']['url']
                feed.picture_large = feed_dict['pic_large']
                feed.username = feed_dict['username']
                feed.website = feed_dict['website']
                # save feed object.
                feed.save()
                # feed_popularity data
                feed_popularity = Feed_Popularity_Model(
                    feed=feed,
                    date_of_creation=timezone.now(),
                    fan_count=feed_dict['likes'],
                    talking_about_count=feed_dict['talking_about_count'],
                )
                feed_popularity.save()

            else:
                print 'No data retrieved for feed {0}'.format(feed_id)
        except Facebook_Feed_Model.DoesNotExist:
            # If feed does not exist at all, raise exception.
            print 'Error: {0} is missing from db'.format(feed_id)
            raise

    def get_feed_data(self, feed, is_insist):
        """
        Returns a Dict object of feed ID. and retrieved feed data.
                """
        if feed.feed_type == 'UP':  # User Profile
	    data_dict = {'feed_id': feed.id, 'data': {}}
            return data_dict
            # Set facebook graph access token to user access token
            token = User_Token_Model.objects.all().order_by('-date_of_creation').first()
            if token:
                print 'token is: %s' % token.token
                self.graph.access_token = token.token
            else:
                print 'No User Access Token was found in the database, skipping'
                data_dict = {'feed_id': feed.id, 'data': {}}
                return data_dict
                # print Exception('No User Access Token was found in the database!')  # TODO:Write as a real exception

            data_dict = {'feed_id': feed.id, 'data': self.fetch_user_profile_object_by_feed_id(feed.vendor_id,
                                                                                               is_insist)}
            pprint(data_dict)
            # Transform data to fit existing public page
            data_dict['data']['username'] = ''.join(
                (data_dict['data']['first_name'], data_dict['data']['last_name'])).lower()
            data_dict['data']['likes'] = 0
            data_dict['data']['talking_about_count'] = 0
            data_dict['data']['about'] = ''
            return data_dict

        elif feed.feed_type == 'PP':  # 'PP - Public Page'
            try:
                # Set facebook graph access token to most up-to-date user token in db
                token = User_Token_Model.objects.first()
                self.graph.access_token = token.token
            except:
                # Fallback: Set facebook graph access token to app access token
                self.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID,
                                                                        settings.FACEBOOK_SECRET_KEY)
                if feed.requires_user_token:
                    # If the Feed is set to require a user-token, and none exist in our db, the feed is skipped.
                    print 'feed %d requires user token, skipping.' % feed.id
                    data_dict = {'feed_id': feed.id, 'data': {}}
                    return data_dict

            # Get the data using the pre-set token
            data_dict = {'feed_id': feed.id, 'data': self.fetch_public_page_object_by_feed_id(feed.vendor_id,
                                                                                              is_insist)}
            return data_dict

        else:  # Deprecated or malfunctioning profile ('NA', 'DP')
            print 'Profile %s is of type %s, skipping.' % (feed.id, feed.feed_type)
            data_dict = {'feed_id': feed.id, 'data': {}}
            return data_dict


    def handle(self, *args, **options):
        """
        Executes fetchperson manage.py command.
        Receives either one feed ID and retrieves the relevant page's data, and updates them in the db,
        or no feed ID and therefore retrieves data for all the feeds.
        """

        is_insist = options['is_insist']

        list_of_feeds = list()
        # Case no args - fetch all feeds
        if len(args) == 0:
            list_of_feeds = [feed for feed in Facebook_Feed_Model.objects.all()]
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
            # get feed properties fro, facebook
            feed_data = self.get_feed_data(feed, is_insist)
            # update fetched dat to feed in database
            if feed_data['data']:
                self.update_feed_data_to_db(feed_data['data'], feed_data['feed_id'])
                self.stdout.write('Successfully fetched feed id {0}'.format(feed.id))
            else:
                self.stdout.write('No data to update for feed id {0}'.format(feed.id))
        
        self.stdout.write('Successfully saved all data in db')
