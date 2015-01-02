from django.db import models
from django.conf import settings

from mks.models import Member, Party
from polyorg.models import Candidate, CandidateList

MEMBER_MODEL = Candidate if settings.IS_ELECTIONS_MODE else Member
PARTY_MODEL = CandidateList if settings.IS_ELECTIONS_MODE else Party
