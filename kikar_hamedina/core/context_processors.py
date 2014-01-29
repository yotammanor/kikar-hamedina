from core.models import Person, Party, Tag
from kikar_hamedina.settings.base import FACEBOOK_APP_ID


def generic(request):
    return {
        'navPersons': Person.objects.all().order_by('name'),
        'navParties': Party.objects.all().order_by('name'),
        'navTags': Tag.objects.all().order_by('name'),
        'facebook_app_id': FACEBOOK_APP_ID,
    }
