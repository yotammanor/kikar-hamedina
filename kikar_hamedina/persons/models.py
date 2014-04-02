from django.db import models

# Create your models here.


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

