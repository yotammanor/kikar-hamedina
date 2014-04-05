from django.db import models

# Create your models here.
from facebook_feeds.models import Facebook_Feed
from django.contrib.contenttypes import generic

class Party(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return self.name


class Person(models.Model):
    name = models.CharField(unique=True, max_length=128)
    slug = models.SlugField(unique=True)
    party = models.ForeignKey('Party', related_name='persons')
    feeds = generic.GenericRelation(Facebook_Feed)

    def __unicode__(self):
        return self.name

