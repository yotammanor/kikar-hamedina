#encoding: utf-8
from django.db import models
from abc import ABCMeta, abstractmethod
from polymorphic import PolymorphicModel
from django.core.mail import  EmailMessage
from jsonfield import JSONField
from django.conf import settings
from facebook_feeds.models import Facebook_Status
import datetime
from django.template.loader import get_template
from django.template import Context

class BaseExecutor(PolymorphicModel):

    @abstractmethod
    def handle_post(self, post, rule):
        pass

class RulesContainer(object):
    def __init__(self):
        self.rules = []

    def add_rule(self, rule):
        self.rules.append(rule)

rulesContainer = RulesContainer()

class BaseRule(PolymorphicModel):
    last_time_analysed = models.DateTimeField()
    executors = models.ManyToManyField(BaseExecutor)

    class Meta:
        abstract = True

    @abstractmethod
    def validate_rule(self, post):
        pass

    @abstractmethod
    def get_rule_name(self):
        pass

    def handle_post(self, post):
        if self.validate_rule(post):
            for executor in self.executors.all():
                executor.handle_post(post, self)

    def handle_new_posts(self):
        statues = Facebook_Status.objects.filter(published__gte = self.last_time_analysed)

        for status in statues:
            self.handle_post(status)
        self.last_time_analysed = datetime.datetime.now()
        self.save()

class LikesRule(BaseRule):
    min_likes = models.IntegerField()
    def validate_rule(self, post):
        if post.like_count > self.min_likes:
            return True
        return False

    def get_rule_name(self):
        return u'כמות לייקים'

rulesContainer.add_rule(LikesRule)

class EmailUpdater(BaseExecutor):
    subscribers = JSONField(default=[])

    def handle_post(self, post, rule):
        print 'sending mails! %s' %(post.id)
        title = u"%s - %s" %(rule.get_rule_name(), post.feed.name)
        msg = EmailMessage(title, self.get_content(post), settings.SERVER_EMAIL, self.subscribers)
        msg.content_subtype = 'html'
        msg.send()

    def get_content(self, post):
        template = get_template('mail_template.html')
        context = Context({ 'post': post })
        htmlContent = template.render(context)
        return htmlContent