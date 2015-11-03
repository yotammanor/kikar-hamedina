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
    user = models.ForeignKey(User, related_name='queries')
    created_at = models.DateTimeField(auto_now=True)
    queryset = models.TextField(null=False, default='')
    title = models.SlugField(unique=True, max_length=64)
    description = models.TextField(null=True)

    @property
    def queryset_q(self):
        return QSerializer(base64=True).loads(self.queryset)

    @property
    def queryset_dict(self):
        return QSerializer(base64=True).loads(self.queryset).__dict__


    def __unicode__(self):
        return "{}, {}".format(self.user, QSerializer(base64=True).loads(self.queryset).__dict__)

    class Meta:
        unique_together = ['user', 'queryset']
