from django.db import models
from django.utils import timezone
from datetime import timedelta

class Party(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True)
    party = models.ForeignKey('Party', related_name='persons')

    def __unicode__(self):
        return self.name


class Facebook_Feed(models.Model):
    FEED_TYPES = (
        ('PP', 'Public Page'),
        ('UP', 'User Profile'),
    )

    person = models.ForeignKey('Person')
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
    talking_about_count = models.IntegerField(default=0)
    fan_count = models.IntegerField(default=0)
    # UserProfile Only
    followers_count = models.IntegerField(default=0)
    friends_count = models.IntegerField(default=0)

    def __unicode__(self):
        return unicode(self.person) + " " + self.vendor_id


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


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=128)
    statuses = models.ManyToManyField(Facebook_Status, related_name='tags')
    is_for_main_display = models.BooleanField(default=True, null=False)

    def __unicode__(self):
        return self.name


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