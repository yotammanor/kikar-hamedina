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
    queryset = models.CharField(max_length=128, null=False, default='')

    def __unicode__(self):
        return "{}, {}".format(self.user, QSerializer(base64=True).loads(self.queryset).__dict__)

    class Meta:
        unique_together = ['user', 'queryset']
