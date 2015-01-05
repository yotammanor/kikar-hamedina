from django.db import models
from django.conf import settings

from mks.models import Member, Party
from polyorg.models import Candidate, CandidateList

IS_ELECTIONS_MODE = getattr(settings, 'IS_ELECTIONS_MODE', False)

MEMBER_MODEL = Candidate if IS_ELECTIONS_MODE else Member
PARTY_MODEL = CandidateList if IS_ELECTIONS_MODE else Party
