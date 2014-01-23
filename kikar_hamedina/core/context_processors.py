from core.models import Person, Party, Tag


def generic(request):
    return {
        'navPersons': Person.objects.all().order_by('name'),
        'navParties': Party.objects.all().order_by('name'),
        'navTags': Tag.objects.all().order_by('name'),
    }
