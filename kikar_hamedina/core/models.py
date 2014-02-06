from django.db import models


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
    person = models.ForeignKey('Person')
    vendor_id = models.TextField(null=True)
    username = models.TextField(null=True, default=None)
    birthday = models.TextField(null=True)
    name = models.TextField(null=True)
    about = models.TextField(null=True)
    talking_about_count = models.IntegerField(default=0)
    fan_count = models.IntegerField(default=0)
    page_url = models.URLField(null=True, max_length=2000)
    pic_large = models.URLField(null=True, max_length=2000)
    pic_square = models.URLField(null=True, max_length=2000)
    website = models.URLField(null=True, max_length=2000)

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
