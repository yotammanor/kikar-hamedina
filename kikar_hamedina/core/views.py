from django.shortcuts import render
from .models import Facebook_Status, Facebook_Feed, Person, Party

def index(request):
    statuses = Facebook_Status.objects.order_by('published')

    persons = Person.objects.all()
    parties = Party.objects.all()
    return render(request, 'core/index.html',
        {'statuses': statuses, 'persons': persons, 'parties': parties, 'breadcrumbs': []})

def person(request, person_id):
    current_person = Person.objects.get(id=person_id)
    print current_person.name

    persons_feeds = Facebook_Feed.objects.filter(person=person_id)
    statuses = Facebook_Status.objects.filter(feed=persons_feeds[0]).order_by('published')

    persons = Person.objects.all()
    parties = Party.objects.all()
    return render(request, 'core/index.html',
        {'statuses': statuses, 'persons': persons, 'parties': parties, 'breadcrumbs': ['Politicians', current_person.name]})

def party(request, party_id):
    current_party = Party.objects.get(id=party_id)

    party_statuses = Facebook_Status.objects.filter(feed__person__party=party_id).order_by('published')
    print party_statuses

    persons = Person.objects.all()
    parties = Party.objects.all()
    return render(request, 'core/index.html',
        {'statuses': party_statuses, 'persons': persons, 'parties': parties, 'breadcrumbs': ['Parties', current_party.name]})
