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
    User_Token as User_Token_Model, \
    Feed_Popularity as Feed_Popularity_Model


class Command(BaseCommand):
    args = '<person_id>'
    help = 'Fetches a person'
    graph = facebook.GraphAPI()

    def fetch_user_profile_object_by_feed_id(self, feed_id):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
        """

        select_user_profile_query = """
            SELECT
                name,
                uid,
                birthday_date,
                profile_url,
                pic_square,
                pic_big,
                username
            FROM
                user
            WHERE
                uid = {0}""".format(feed_id)
        # '508516607'
        return self.graph.fql(query=select_user_profile_query)


    def fetch_page_object_by_feed_id(self, feed_id):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
                """
        select_public_page_info_query = """
                    SELECT
                        about,
                        birthday,
                        fan_count,
                        name,
                        page_id,
                        page_url,
                        pic_large,
                        pic_square,
                        talking_about_count,
                        username,
                        website
                    FROM
                        page
                    WHERE
                        page_id={0}""".format(feed_id)
        return self.graph.fql(query=select_public_page_info_query)


    def update_feed_data_to_db(self, feed_data, feed_id):
        """
        Receives a single Facebook_Page data object as retrieved from facebook-sdk,
        and updates the data into Facebook_Feed in the db.
                """
        #Create a datetime object from int received in status_object
        # current_time_of_update = datetime.datetime.fromtimestamp(feed_data['updated_time'],tz=timezone.utc)
        try:
            if feed_data:
                feed_dict = feed_data[0]
                # If post_id already exists in DB
                feed = Facebook_Feed_Model.objects.get(id=feed_id)
                # Assuming retrieved data from facebook is always more up-to-date than our data
                feed.about = feed_dict['about']
                feed.birthday = feed_dict['birthday']
                feed.name = feed_dict['name']
                feed.page_url = feed_dict['page_url']
                feed.pic_large = feed_dict['pic_large']
                feed.pic_square = feed_dict['pic_square']
                feed.username = feed_dict['username']
                feed.website = feed_dict['website']
                # save feed object.
                feed.save()
                # feed_popularity data
                feed_popularity = Feed_Popularity_Model(
                    feed=feed,
                    date_of_creation=timezone.now(),
                    fan_count=feed_dict['fan_count'],
                    talking_about_count=feed_dict['talking_about_count'],
                )
                feed_popularity.save()

            else:
                print 'No data retrieved for feed {0}'.format(feed_id)
        except Facebook_Feed_Model.DoesNotExist:
            # If feed does not exist at all, raise exception.
            print 'Error: {0} is missing from db'.format(feed_id)
            raise


    def get_feed_data(self, feed):
        """
        Returns a Dict object of feed ID. and retrieved feed data.
        """
        if feed.feed_type == 'UP':  # User Profile
            # Set facebook graph access token to user access token
            token = User_Token_Model.objects.all().order_by('-date_of_creation').first()
            if token:
                print 'token is: %s' % token.token
            else:
                raise Exception('No User Access Token was found in the database!')  #TODO:Write as a real exception
            self.graph.access_token = token.token
            data_dict = {'feed_id': feed.id, 'data': self.fetch_user_profile_object_by_feed_id(feed.vendor_id)}
            pprint(data_dict)
            # Transform data to fit existing public page
            data_dict['data'][0]['fan_count'] = 0
            data_dict['data'][0]['talking_about_count'] = 0
            data_dict['data'][0]['about'] = ''
            data_dict['data'][0]['page_url'] = data_dict['data'][0]['profile_url']
            data_dict['data'][0]['website'] = data_dict['data'][0]['profile_url']
            data_dict['data'][0]['pic_large'] = data_dict['data'][0]['pic_big']
            data_dict['data'][0]['birthday'] = data_dict['data'][0]['birthday_date']
            return data_dict
        else:  # 'PP - Public Page'
            # Set facebook graph access token to app access token
            self.graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
            data_dict = {'feed_id': feed.id, 'data': self.fetch_page_object_by_feed_id(feed.vendor_id)}
            return data_dict


    def handle(self, *args, **options):
        """
        Executes fetchperson manage.py command.
        Receives either one feed ID and retrieves the relevant page's data, and updates them in the db,
        or no feed ID and therefore retrieves data for all the feeds.
        """
        feeds_data = []
        # Case no args - fetch all feeds
        if len(args) == 0:
            for feed in Facebook_Feed_Model.objects.all():
                self.stdout.write('Working on feed: {0}.'.format(feed.pk))
                feeds_data.append(self.get_feed_data(feed))
            self.stdout.write('Successfully fetched all')

        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])

            try:
                feed = Facebook_Feed_Model.objects.get(pk=feed_id)
                self.stdout.write('Successfully fetched feed id {0}'.format(feed_id))
            except Facebook_Feed_Model.DoesNotExist:
                raise CommandError('Feed "%s" does not exist' % feed_id)

            feeds_data.append(self.get_feed_data(feed))

        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')

        # Update fetched data to feed in database
        for feed_data in feeds_data:
            self.update_feed_data_to_db(feed_data['data'], feed_data['feed_id'])

        self.stdout.write('Successfully saved all statuses to db.')