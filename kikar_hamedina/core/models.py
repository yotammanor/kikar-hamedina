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
    vendor_id = models.CharField(unique=True, max_length=128)
    username = models.CharField(null=True, max_length=128)
    birthday = models.CharField(null=True, max_length=128)
    name = models.CharField(null=True, max_length=256)
    talking_about_count = models.IntegerField(default=0)
    fan_count = models.IntegerField(default=0)
    page_url = models.URLField(null=True)
    pic_large = models.URLField(null=True)
    pic_square = models.URLField(null=True)
    website = models.URLField(null=True)
    about = models.TextField(null=True)

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
        "Returns a link to this post."
        split_status_id = self.status_id.split('_')
        return 'https://www.facebook.com/%d/posts/%d' % (split_status_id[0], split_status_id[1])


class Tag(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=False, max_length=128)
    description = models.TextField()
    statuses = models.ManyToManyField(Facebook_Status, related_name='tags')

    def __unicode__(self):
        return self.name
