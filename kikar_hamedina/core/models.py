from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from mks.models import Member, Party
from polyorg.models import Candidate, CandidateList
from core.qserializer import QSerializer

IS_ELECTIONS_MODE = getattr(settings, 'IS_ELECTIONS_MODE', False)

MEMBER_MODEL = Candidate if IS_ELECTIONS_MODE else Member
PARTY_MODEL = CandidateList if IS_ELECTIONS_MODE else Party


class UserSearch(models.Model):

    SERIALIZED_EMPTY_Q_OBJECT = 'eyJjb25uZWN0b3IiOiAiQU5EIiwgIm5lZ2F0ZWQiOiBmYWxzZSwgImNoaWxkcmVuIjogW119'  # Q()

    user = models.ForeignKey(User, related_name='queries')
    created_at = models.DateTimeField(auto_now=True)
    queryset = models.TextField(null=False, default=SERIALIZED_EMPTY_Q_OBJECT)
    path = models.TextField(null=False, default='')
    title = models.SlugField(unique=True, max_length=64)
    description = models.TextField(null=True)
    date_range = models.TextField(null=True)
    order_by = models.TextField(null=True)

    @property
    def queryset_q(self):
        return self.queryset and QSerializer(base64=True).loads(self.queryset)

    @property
    def queryset_dict(self):
        return self.queryset and QSerializer(base64=True).loads(self.queryset).__dict__

    @property
    def date_range_q(self):
        return self.date_range and QSerializer(base64=True).loads(self.date_range)

    @property
    def date_range_dict(self):
        return self.date_range and QSerializer(base64=True).loads(self.date_range).__dict__

    def __unicode__(self):
        return "{}, {}".format(self.user, self.title)
