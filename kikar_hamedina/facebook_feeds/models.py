import datetime
from unidecode import unidecode

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django_pandas.managers import DataFrameManager

from facebook_feeds.managers import Facebook_StatusManager, Facebook_FeedManager

INDICATIVE_TEXTS_FOR_COMMENT_IN_STORY_FIELD = ['on his own',
                                               'on their own',
                                               'on her own',
                                               'likes a link',
                                               'likes a photo',
                                               'likes a video',
                                               'commented on this',

                                               ]


class Facebook_Persona(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()
    main_feed = models.SmallIntegerField(null=True, default=0)

    @property
    def get_main_feed(self):
        try:
            return Facebook_Feed.objects.get(id=self.main_feed)
        except:
            return None  # TODO: What should we return here when no main feed is defined/ no feeds exist?

    def __unicode__(self):
        return "Facebook_Persona: " + self.content_type + " " + str(self.object_id)


class Facebook_Feed(models.Model):
    FEED_TYPES = (
        ('PP', 'Public Page'),
        ('UP', 'User Profile'),
        ('NA', 'Unavailable Profile'),
        ('DP', 'Deprecated Profile'),
    )

    DEFAULT_DAYS_BACK_FOR_POPULARITY_DIF = getattr(settings, 'DEFAULT_DAYS_BACK_FOR_POPULARITY_DIF', 7)

    persona = models.ForeignKey('Facebook_Persona', related_name='feeds')
    vendor_id = models.TextField(null=True)
    username = models.TextField(null=True, default=None)
    birthday = models.TextField(null=True)
    name = models.TextField(null=True)
    link = models.URLField(null=True, max_length=2000)
    picture_square = models.URLField(null=True, max_length=2000)
    picture_large = models.URLField(null=True, max_length=2000)
    feed_type = models.CharField(null=False, max_length=2, choices=FEED_TYPES, default='PP')
    requires_user_token = models.BooleanField(default=False, null=False)
    is_current = models.BooleanField(default=True, null=False)
    current_fan_count = models.IntegerField(default=0, null=False)

    # Public Page Only
    about = models.TextField(null=True, default='')
    website = models.URLField(null=True, max_length=2000)

    objects = DataFrameManager()

    current_feeds = Facebook_FeedManager()

    class Meta:
        ordering = ['feed_type']  # This will create a preference for Public Page over User Profile when both exist.

    def __unicode__(self):
        return unicode(self.username) + " " + self.vendor_id

    @property
    def get_current_fan_count(self):
        popularity = 0
        if self.feed_type == 'PP':
            try:
                popularity = Feed_Popularity.objects.filter(feed=self).latest('date_of_creation').fan_count
            except Feed_Popularity.DoesNotExist:
                pass
        return popularity

    def popularity_dif(self, days_back, return_value='all_dict'):

        dif_dict = {'fan_count_dif_nominal': 0,
                    'fan_count_dif_growth_rate': 0.0,
                    'fan_count_at_requested_date': 0,
                    'is_interpolated': False,
                    'date_of_value': datetime.date.today()}

        dif_dict_default = dif_dict.copy()

        is_interpolated = False

        feed_current_count = self.current_fan_count
        asked_for_date_of_value = timezone.now() - datetime.timedelta(days=days_back)

        try:
            popularity_history_timeseries = self.feed_popularity_set.to_timeseries('fan_count', index='date_of_creation')
            first_value = popularity_history_timeseries.iloc[-1].name.to_pydatetime()
            last_value = popularity_history_timeseries.iloc[0].name.to_pydatetime()

            if (asked_for_date_of_value < first_value) or \
                    (asked_for_date_of_value > last_value) or \
                    (popularity_history_timeseries.count().fan_count <= 1):
                # if history starts after date of request, or there isn't enough data, don't extrapolate.
                fan_count_at_requested_date = 0

            else:
                resampled_history_raw = popularity_history_timeseries.resample('D')
                if resampled_history_raw.loc[asked_for_date_of_value.date()].isnull().fan_count:
                    # if requested date's data is missing - interpolate from existing data
                    is_interpolated = True
                    resampled_history_interpolated = resampled_history_raw.interpolate()
                    fan_count_at_requested_date = resampled_history_interpolated.loc[asked_for_date_of_value.date()].fan_count
                else:
                    fan_count_at_requested_date = resampled_history_raw.loc[asked_for_date_of_value.date()].fan_count

            fan_count_dif_nominal = int(feed_current_count) - fan_count_at_requested_date
            if fan_count_at_requested_date != 0:
                fan_count_dif_growth_rate = float(fan_count_dif_nominal) / fan_count_at_requested_date
            else:
                fan_count_dif_growth_rate = 0.0

            dif_dict['fan_count_dif_nominal'] = fan_count_dif_nominal
            dif_dict['fan_count_at_requested_date'] = fan_count_at_requested_date
            dif_dict['date_of_value'] = asked_for_date_of_value
            dif_dict['is_interpolated'] = is_interpolated
            dif_dict['fan_count_dif_growth_rate'] = fan_count_dif_growth_rate
        except IndexError:
            dif_dict = dif_dict_default

        finally:
            if return_value == 'all_dict':
                return dif_dict
            else:
                try:
                    return dif_dict[return_value]
                except KeyError:
                    return dif_dict


    @property
    def popularity_dif_week_nominal(self, days_back=DEFAULT_DAYS_BACK_FOR_POPULARITY_DIF):
        return self.popularity_dif(days_back)['fan_count_dif_nominal']

    @property
    def popularity_dif_week_growth_rate(self, days_back=DEFAULT_DAYS_BACK_FOR_POPULARITY_DIF):
        return self.popularity_dif(days_back)['fan_count_dif_growth_rate']

class Feed_Popularity(models.Model):
    feed = models.ForeignKey('Facebook_Feed')
    date_of_creation = models.DateTimeField(default=timezone.now())
    # PublicPage Only
    talking_about_count = models.IntegerField(default=0)
    fan_count = models.IntegerField(default=0)
    # UserProfile Only
    followers_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)

    objects = DataFrameManager()

    class Meta:
        ordering = ['-date_of_creation']

    def __unicode__(self):
        return unicode(self.feed) + " " + str(self.date_of_creation)
        # strftime("%Y_%M_%D_%H:%m:%s", self.date_of_creation)


class Facebook_Status(models.Model):
    TYPE_CHOICES = (
        (11, 'Group created'),
        (12, 'Event created'),
        (46, 'Status update'),
        (56, 'Post on wall from another user'),
        (66, 'Note created'),
        (80, 'Link posted'),
        (128, 'Video posted'),
        (247, 'Photos posted'),
        (237, 'App story'),
        (257, 'Comment created'),
        (272, 'App story'),
        (285, 'Checkin to a place'),
        (308, 'Post in Group'),
        (0, 'Kikar - missing data')
    )

    feed = models.ForeignKey('Facebook_Feed')
    status_id = models.CharField(unique=True, max_length=128)
    content = models.TextField()
    like_count = models.PositiveIntegerField(null=True)
    comment_count = models.PositiveIntegerField(null=True)
    share_count = models.PositiveIntegerField(null=True)
    published = models.DateTimeField()
    updated = models.DateTimeField()
    status_type = models.CharField(null=True, default=None, max_length=128)
    story = models.TextField(null=True)
    story_tags = models.TextField(null=True)
    is_comment = models.BooleanField(default=False)

    objects = Facebook_StatusManager()  # Filters out all rows with is_comment=True. Inherits from DataFrame Manager.
    objects_no_filters = DataFrameManager()  # default Manager with DataFrameManager, does not filter out is_comment=True.

    def __unicode__(self):
        return self.status_id

    @property
    def get_link(self):
        """
        Returns a link to this post.
        """
        split_status_id = self.status_id.split('_')
        return 'https://www.facebook.com/%s/posts/%s' % (split_status_id[0], split_status_id[1])

    @property
    def has_attachment(self):
        try:
            if self.attachment:
                return True
            else:
                return False
        except:
            return False

    @property
    def set_is_comment(self):
        """
        A Method for deciding whether a status is a comment or not, according to the method's logic.
        Returns True or False.
        """
        # Some formatting and printing
        if self.story:
            story_string = unidecode(self.story)
        else:
            story_string = ''

        # print 'status db id:', self.id
        # print 'story string:', story_string

        # Check for non-mk users mentioned within status's story tags
        if self.story_tags:
            # has a story with the style of <user> commented on <feed>'s status
            # print self.story_tags, type(self.story_tags)
            story_tags_eval = eval(str(self.story_tags))
            try:
                for tag in story_tags_eval.values():
                    for dic in tag:
                        feed_in_tag = Facebook_Feed.objects.filter(vendor_id=dic['id'])
                        if not feed_in_tag:
                            # the mentioned user is not an mk
                            # print 'True'
                            return True
            except:
                # print 'True'
                return True

            # print 'True'
            return True

        # Check for strings indicative of comment activity
        found_text = []
        for text in INDICATIVE_TEXTS_FOR_COMMENT_IN_STORY_FIELD:
            # print 'trying', text
            if text in story_string:
                # print 'found'
                found_text.append(text)
            # else:
                # print 'not found'
        if found_text:
            # print 'True'
            return True
        else:
            # print 'False'
            return False


status_with_photo = '161648040544835_720225251353775'
status_with_youtube_link = '161648040544835_723225304387103'
status_with_link_to_newspaper = '161648040544835_719797924729841'
status_with_no_multimedia = '161648040544835_718801471496153'

ATTACHMENT_MEDIA_TYPES = (
    ('status', 'Status'),
    ('video', 'Video'),
    ('photo', 'Photo'),
    ('link', 'Link'),
)

# """
#
# https://developers.facebook.com/docs/reference/fql/stream/
#
# The type of this story. Possible values are:
# 11 - Group created
# 12 - Event created
# 46 - Status update    # Relevant
# 56 - Post on wall from another user
# 66 - Note created
# 80 - Link posted     # Relevant
# 128 -Video posted      # Relevant
# 247 - Photos posted     # Relevant
# 237 - App story
# 257 - Comment created
# 272 - App story
# 285 - Checkin to a place
# 308 - Post in Group
# """


class Facebook_Status_Attachment(models.Model):
    status = models.OneToOneField(Facebook_Status, related_name='attachment')
    name = models.TextField(null=True)  # name
    caption = models.TextField(null=True)  # caption
    description = models.TextField(null=True)  # description
    link = models.TextField(null=False)  # link
    facebook_object_id = models.CharField(unique=False, null=True,
                                          max_length=128)  # object_id (exists only for internal links)
    type = models.CharField(null=True, choices=ATTACHMENT_MEDIA_TYPES, max_length=16)  # type
    picture = models.TextField(null=True)  # picture

    @property
    def is_internal_link(self):
        return 'https://www.facebook.com/' in self.link


class User_Token(models.Model):
    token = models.CharField(max_length=256, unique=True)
    user_id = models.TextField(unique=True)
    date_of_creation = models.DateTimeField(default=timezone.now())
    date_of_expiration = models.DateTimeField(default=timezone.now() + timezone.timedelta(days=60))
    feeds = models.ManyToManyField(Facebook_Feed, related_name='tokens')
    # is_expired = models.BooleanField(default=False)

    @property
    def is_expired(self):
        if self.date_of_expiration - timezone.now() <= 0:
            return True
        else:
            return False

    def __unicode__(self):
        return 'token_' + self.user_id


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=128)
    statuses = models.ManyToManyField(Facebook_Status, related_name='tags')
    is_for_main_display = models.BooleanField(default=True, null=False)

    def __unicode__(self):
        return self.name

