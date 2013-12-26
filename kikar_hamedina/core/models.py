from django.db import models


class Party(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True)
    party = models.ForeignKey('Party')

    def __unicode__(self):
        return self.name


class Facebook_Feed(models.Model):
    person = models.ForeignKey('Person')
    vendor_id = models.CharField(unique=True, max_length=128)

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

    def __unicode__(self):
        return self.status_id

class Tag(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True, max_length=128)
    description = models.TextField()
    statuses = models.ManyToManyField(Facebook_Status)

    def __unicode__(self):
        return self.name