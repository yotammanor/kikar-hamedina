from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# Create your models here.


class Facebook_Feed_Generic(models.Model):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey()


class Facebook_Feed(Facebook_Feed_Generic):
    FEED_TYPES = (
        ('PP', 'Public Page'),
        ('UP', 'User Profile'),
    )

    # person = models.ForeignKey('persons.Person')
    vendor_id = models.TextField(null=True)
    username = models.TextField(null=True, default=None)
    birthday = models.TextField(null=True)
    name = models.TextField(null=True)
    page_url = models.URLField(null=True, max_length=2000)
    pic_large = models.URLField(null=True, max_length=2000)
    pic_square = models.URLField(null=True, max_length=2000)
    feed_type = models.CharField(null=False, max_length=2, choices=FEED_TYPES, default='PP')
    # Public Page Only
    about = models.TextField(null=True, default='')
    website = models.URLField(null=True, max_length=2000)

    class Meta:
        ordering = ['feed_type']  # This will create a preference for Public Page over User Profile when both exist.

    def __unicode__(self):
        return unicode(self.username) + " " + self.vendor_id

    @property
    def get_current_fan_count(self):
        return Feed_Popularity.objects.filter(feed=self).latest('date_of_creation').fan_count

    current_fan_count = get_current_fan_count


class Feed_Popularity(models.Model):
    feed = models.ForeignKey('Facebook_Feed')
    date_of_creation = models.DateTimeField(default=timezone.now())
    # PublicPage Only
    talking_about_count = models.IntegerField(default=0)
    fan_count = models.IntegerField(default=0)
    # UserProfile Only
    followers_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)

    class Meta:
        ordering = ['-date_of_creation']

    def __unicode__(self):
        return unicode(self.feed) + " " + str(self.date_of_creation)
               # strftime("%Y_%M_%D_%H:%m:%s", self.date_of_creation)


class Facebook_Status(models.Model):
    feed = models.ForeignKey('Facebook_Feed')
    status_id = models.CharField(unique=True, max_length=128)
    content = models.TextField()
    like_count = models.PositiveIntegerField(null=True)
    comment_count = models.PositiveIntegerField(null=True)
    share_count = models.PositiveIntegerField(null=True)
    published = models.DateTimeField()
    updated = models.DateTimeField()

    def __unicode__(self):
        return self.status_id

    @property
    def get_link(self):
        """
        Returns a link to this post.
        """
        split_status_id = self.status_id.split('_')
        return 'https://www.facebook.com/%d/posts/%d' % (split_status_id[0], split_status_id[1])

    @property
    def has_attachment(self):
        try:
            if self.attachment:
                return True
            else:
                return False
        except:
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
    name = models.TextField(null=True)  #name
    caption = models.TextField(null=True)  #caption
    description = models.TextField(null=True)  #description
    link = models.URLField(null=True, max_length=512)  #href
    facebook_object_id = models.CharField(unique=False, null=True, max_length=128)  #fb_object_id (exists only for internal links)

    @property
    def is_internal_link(self):
        return 'https://www.facebook.com/' in self.link

    @property
    def get_link(self):
        if self.link:
            return self.link
        elif self.media.count() == 1:
            return self.media.first().link
        else:
            return None


class Facebook_Status_Attachment_Media(models.Model):
    attachment = models.ForeignKey(Facebook_Status_Attachment, related_name='media')
    type = models.CharField(null=True, choices=ATTACHMENT_MEDIA_TYPES, max_length=16)  #type
    link = models.URLField(null=True, max_length=512)  #href
    alt = models.TextField(null=True) #alt
    picture = models.URLField(null=True, max_length=512)  #picture
    thumbnail = models.URLField(null=True, max_length=512)  # src
    owner_id = models.TextField(null=True)  # photo.owner

    class Meta:
        unique_together = ('attachment', 'link')

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

