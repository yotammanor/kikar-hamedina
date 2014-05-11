import datetime
from optparse import make_option
from collections import defaultdict
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
    Facebook_Status_Attachment as Facebook_Status_Attachment_Model, \
    Facebook_Status_Attachment_Media as Facebook_Status_Attachment_Media_Model

LENGTH_OF_EMPTY_ATTACHMENT_JSON = 21

DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN = 1000
DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN = 20


class Command(BaseCommand):
    args = '<feed_id>'
    help = 'Fetches a feed'
    option_initial = make_option('-i',
                                 '--initial',
                                 action='store_true',
                                 dest='initial',
                                 default=False,
                                 help='Flag initial runs fql query with limit of {0} instead of regular limit of {1}.'
                                 .format(DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN,
                                         DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN)
    )
    option_force_attachment_update = make_option('-a',
                                                 '--force-attachment-update',
                                                 action='store_true',
                                                 dest='force-attachment-update',
                                                 default=False,
                                                 help='Use this flag to force updating of status attachment'
    )
    option_list_helper = list()
    for x in BaseCommand.option_list:
        option_list_helper.append(x)
    option_list_helper.append(option_initial)
    option_list_helper.append(option_force_attachment_update)
    option_list = tuple(option_list_helper)

    graph = facebook.GraphAPI()

    def fetch_status_objects_from_feed(self, feed_id, fql_limit):
        """
        Receives a feed_id for a facebook
        Returns a facebook-sdk fql query, with all status objects published by the page itself.
                """
        select_self_published_status_query = """
                SELECT
                    post_id, message, created_time, like_info, comment_info, share_count, updated_time, attachment, type
                FROM
                    stream
                WHERE
                    source_id IN ({0}) AND actor_id IN ({0})
                LIMIT {1}""".format(feed_id, fql_limit)
        tryNumber = 1
        while tryNumber < 4:
            try:
                returnStatuses = self.graph.fql(query=select_self_published_status_query)
                return returnStatuses
            except:
                warning_msg = "Failed first attempt for feed #({0}) from FB API.".format(feed_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                tryNumber += 1
        error_msg = "Failed three attempts for feed #({0}) from FB API.".format(feed_id)
        logger = logging.getLogger('django.request')
        logger.warning(error_msg)
        return []

    @staticmethod
    def insert_status_attachment(status, status_object):
        attachment_defaultdict = defaultdict(str, status_object['attachment'])
        attachment = Facebook_Status_Attachment_Model(
            status=status,
            name=attachment_defaultdict['name'],
            caption=attachment_defaultdict['caption'],
            description=attachment_defaultdict['description'],
            link=attachment_defaultdict['href'],
            facebook_object_id=attachment_defaultdict['fb_object_id']
        )
        attachment.save()
        # add all media files related to attachment
        for media_file in status_object['attachment']['media']:
            media_file_defaultdict = defaultdict(str, media_file)

            media = Facebook_Status_Attachment_Media_Model(
                attachment=attachment,
                type=media_file_defaultdict['type'],
                link=media_file_defaultdict['href'],
                alt=media_file_defaultdict['alt'],
                thumbnail=media_file_defaultdict['src'],
            )
            if media.type == 'photo':
                media.picture = media_file_defaultdict['picture']
                media.owner_id = media_file_defaultdict['photo']['owner']
            media.save()


    @staticmethod
    def get_unique_link_for_media(attachment, i, media_file):
        media_file_defaultdict = defaultdict(str, media_file)
        if media_file_defaultdict['href']:
            unique_link = media_file_defaultdict['href']
        elif 'music' in media_file_defaultdict.keys():
            unique_link = media_file_defaultdict['music']['source_url']
        else:
            unique_link = '%s_media_%s' % (attachment.status.status_id, i)
        return media_file_defaultdict, unique_link

    @staticmethod
    def update_status_attachment(attachment, status_object):

        #Update relevant attachment fields
        attachment_defaultdict = defaultdict(str, status_object['attachment'])
        attachment.name = attachment_defaultdict['name']
        attachment.caption = attachment_defaultdict['caption']
        attachment.description = attachment_defaultdict['description']
        attachment.link = attachment_defaultdict['href']
        attachment.facebook_object_id = attachment_defaultdict['fb_object_id']
        attachment.save()

        # add or update all media files related to attachment
        try:
            for i, media_file in enumerate(attachment_defaultdict['media']):

                media_file_defaultdict, unique_link = Command.get_unique_link_for_media(attachment, i, media_file)
                media, created = Facebook_Status_Attachment_Media_Model.objects.get_or_create(attachment=attachment,
                                                                                              link=unique_link)
                media.type = media_file_defaultdict['type']
                media.link = media_file_defaultdict['href']
                media.alt = media_file_defaultdict['alt']
                media.thumbnail = media_file_defaultdict['src']
                if media.type == 'photo':
                    media.picture = media_file_defaultdict['picture']
                    media.owner_id = media_file_defaultdict['photo']['owner']
                media.save()
        except:
            raise
        #delete a media if no longer appears in retrieved attachment but appears in db
        list_of_links = list()
        for i, media_file in enumerate(status_object['attachment']['media']):
            media_file_defaultdict, unique_link = Command.get_unique_link_for_media(attachment, i, media_file)
            list_of_links.append(unique_link)

        for media in attachment.media.all():
            if media.link not in list_of_links:
                print '%s!=%s' % (media.link, list_of_links)
                media.delete()

        # if all media are deleted, and attachment has no link - then there's no attachment, and it must be deleted
        if not attachment.link and not attachment.media.all():
            print 'deleting attachment'
            attachment.delete()

    def create_or_update_attachment(self, status, status_object):
        """
        If attachment exists, create or update all relevant fields.
        """
        print status.status_id
        if len(str(status_object['attachment'])) > LENGTH_OF_EMPTY_ATTACHMENT_JSON:
            attachment, created = Facebook_Status_Attachment_Model.objects.get_or_create(
                status=status)
            print 'I have an attachment. Created now: %s; Length of data: %d; id: %s' % (
                created, len(str(status_object['attachment'])), status.status_id)
            self.update_status_attachment(attachment, status_object)
        else:
            print 'i don''t have an attachment; Length of data: %d; id: %s' % (
                len(str(status_object['attachment'])), status.status_id)

    def insert_status_object_to_db(self, status_object, feed_id, options):
        """
        Receives a single status object as retrieved from facebook-sdk, an inserts the status
        to the db.
                """
        #Create a datetime object from int received in status_object
        current_time_of_update = datetime.datetime.fromtimestamp(status_object['updated_time'],
                                                                 tz=timezone.utc)

        try:
            # If post_id already exists in DB
            status = Facebook_Status_Model.objects.get(status_id=status_object['post_id'])
            if status.updated < current_time_of_update:
                # If post_id exists but of earlier update time, fields are updated.
                status.content = status_object['message']
                status.like_count = status_object['like_info']['like_count']
                status.comment_count = status_object['comment_info']['comment_count']
                status.share_count = status_object['share_count']
                status.updated = current_time_of_update
                # update attachment data
                self.create_or_update_attachment(status, status_object)
            elif options['force-attachment-update']:
                # force update of attachment, regardless of time
                status.save()
                self.create_or_update_attachment(status, status_object)
            # If post_id exists but of equal or later time (unlikely, but may happen), disregard
            # Should be an else here for this case but as it is, just disregard
        except Facebook_Status_Model.DoesNotExist:
            # If post_id does not exist at all, create it from data.
            status = Facebook_Status_Model(feed_id=feed_id,
                                           status_id=status_object['post_id'],
                                           content=status_object['message'],
                                           like_count=status_object['like_info']['like_count'],
                                           comment_count=status_object['comment_info']['comment_count'],
                                           share_count=status_object['share_count'],
                                           published=datetime.datetime.fromtimestamp(
                                               int(status_object['created_time']),tz=timezone.utc),
                                           updated=current_time_of_update)
            if len(str(status_object['attachment'])) > LENGTH_OF_EMPTY_ATTACHMENT_JSON:
                #There's an attachment
                status.save()
                self.insert_status_attachment(status, status_object)
        finally:
            # save status object.
            status.save()

    def get_feed_statuses(self, feed, fql_limit):
        """
        Returns a Dict object of feed ID. and retrieved status objects.
                """
        if feed.feed_type == 'PP':
            # Set facebook graph access tokens as app access token
            self.graph.access_token = facebook.get_app_access_token(
                settings.FACEBOOK_APP_ID,
                settings.FACEBOOK_SECRET_KEY
            )
            return {'feed_id': feed.id, 'statuses': self.fetch_status_objects_from_feed(feed.vendor_id, fql_limit)}

        else:  # feed_type == 'UP' - User Profile
            # Set facebook graph access token to user access token
            token = User_Token_Model.objects.filter(feeds__id=feed.id).order_by('-date_of_creation').first()
            if not token:
                print 'No Token found for User Profile %s' % feed
                return {'feed_id': feed.id, 'statuses': []}
            else:
                print 'using token by user_id: %s' % token.user_id
                self.graph.access_token = token.token
                return {'feed_id': feed.id, 'statuses': self.fetch_status_objects_from_feed(feed.vendor_id, fql_limit)}

    def handle(self, *args, **options):
        """
        Executes fetchfeed manage.py command.
        Receives either one feed ID and retrieves Statuses for that feed,
        or no feed ID and therefore retrieves all Statuses for all the feeds.
        """
        feeds_statuses = []
        if options['initial']:
            fql_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_INITIAL_RUN
        else:
            fql_limit = DEFAULT_STATUS_SELECT_LIMIT_FOR_REGULAR_RUN
        print 'Variable fql_limit set to: {0}.'.format(fql_limit)

        # Case no args - fetch all feeds
        if len(args) == 0:
            for feed in Facebook_Feed_Model.objects.all():
                self.stdout.write('Working on feed: {0}.'.format(feed.pk))
                feed_statuses = self.get_feed_statuses(feed, fql_limit)
                self.stdout.write('Successfully fetched feed: {0}.'.format(feed.pk))
                for status in feed_statuses['statuses']:
                    self.insert_status_object_to_db(status, feed_statuses['feed_id'], options)
                self.stdout.write('Successfully written feed: {0}.'.format(feed.pk))
                info_msg = "Successfully updated feed: {0}.".format(feed.pk)
                logger = logging.getLogger('django')
                logger.info(info_msg)

        # Case arg exists - fetch feed by id supplied
        elif len(args) == 1:
            feed_id = int(args[0])

            try:
                feed = Facebook_Feed_Model.objects.get(pk=feed_id)
            except Facebook_Feed_Model.DoesNotExist:
                warning_msg = "Feed #({0}) does not exist.".format(feed_id)
                logger = logging.getLogger('django')
                logger.warning(warning_msg)
                raise CommandError('Feed "%s" does not exist' % feed_id)

            feed_statuses = self.get_feed_statuses(feed, fql_limit)
            for status in feed_statuses['statuses']:
                self.insert_status_object_to_db(status, feed_statuses['feed_id'], options)
            self.stdout.write('Successfully written feed: {0}.'.format(feed.id))
            info_msg = "Successfully updated feed: {0}.".format(feed_id)
            logger = logging.getLogger('django')
            logger.info(info_msg)

        # Case invalid args
        else:
            raise CommandError('Please enter a valid feed id')
        info_msg = "Successfully saved all statuses to db"
        logger = logging.getLogger('django')
        logger.info(info_msg)
        self.stdout.write('Successfully saved all statuses to db.')
