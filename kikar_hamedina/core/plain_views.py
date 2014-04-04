from django.core.exceptions import FieldError
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.views.generic.list import ListView
from django.template.defaultfilters import slugify
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag
from django.db.models import Count
from django.conf import settings
import datetime, facebook, os, urllib2, json

NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY = 3

NUMBER_OF_TAGS_TO_PRESENT = 3


class AllStatusesView(ListView):
    model = Facebook_Status
    template_name = 'core/all_results.html'
    # paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super(AllStatusesView, self).get_context_data(**kwargs)
        context['navPersons'] = Person.objects.all().order_by('name')
        context['navParties'] = Party.objects.all().order_by('name')
        context['navTags'] = Tag.objects.all().order_by('name')
        context['context_object'] = self.kwargs['context_object']
        context['side_bar_list'] = Person.objects.filter(
            facebook_feed__facebook_status__published__gte=(
                datetime.date.today() - datetime.timedelta(days=3))).distinct()
        return context


class HomepageView(ListView):
    model = Tag
    template_name = 'core/homepage.html'

    def get_queryset(self):
        queryset = Tag.objects.filter(is_for_main_display=True).annotate(number_of_posts=Count('statuses')).order_by(
            '-number_of_posts')[:NUMBER_OF_TAGS_TO_PRESENT]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HomepageView, self).get_context_data(**kwargs)
        wrote_about_tag = dict()
        for tag in context['object_list']:
            wrote_about_tag[tag] = Facebook_Feed.objects.filter(
                facebook_status__tags__id=tag.id).distinct().order_by('-fan_count')[:NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY]
        context['wrote_about_tag'] = wrote_about_tag
        return context


class SearchView(ListView):
    model = Facebook_Status
    # paginate_by = 10
    context_object_name = 'filtered_statuses'
    template_name = "core/search.html"

    def get_queryset(self):
        people = []
        if 'people' in self.request.GET.keys():
            people = [int(person_id) for person_id in self.request.GET['people'].split(',')]
        if 'parties' in self.request.GET.keys():
            parties_ids = [int(party_id) for party_id in self.request.GET['parties'].split(',')]
            parties = Party.objects.filter(id__in=parties_ids)
            for party in parties:
                for person in party.persons.all():
                    if person.id not in people:
                        people.append(person.id)

        tags = []
        if 'tags' in self.request.GET.keys():
            tags = [int(tag_id) for tag_id in self.request.GET['tags'].split(',')]


        if not people and not tags:
            queryset = Facebook_Status.objects.filter(feed=-1)
        elif people and not tags:
            queryset = Facebook_Status.objects.filter(feed__in=people).order_by('-published')
        elif not people and tags:
            queryset = Facebook_Status.objects.filter(tags__in=tags).order_by('-published')
        else:
            queryset = Facebook_Status.objects.filter(feed__in=people,tags__in=tags).order_by('-published')

        # queryset = Facebook_Status.objects.filter(feed__in=range(100),tags__in=[]).order_by('-published')
        return queryset

    def get_context_data(self, **kwargs):

        people_str = ""
        if 'people' in self.request.GET.keys():
            people = [int(feed_id) for feed_id in self.request.GET['people'].split(',')]
            for person_id in people:
                people_str+= Person.objects.get(pk=feed_id).name
                people_str+= ","
            people_str = people_str[:len(people_str) - 1]

        parties_str = ""
        if 'parties' in self.request.GET.keys():
            parties_ids = [int(party_id) for party_id in self.request.GET['parties'].split(',')]
            for party_id in parties_ids:
                parties_str += Party.objects.get(pk=party_id).name
                parties_str += ","
            parties_str = parties_str[:len(parties_str) - 1]

        tags_str = ""
        if 'tags' in self.request.GET.keys():
            tags = [int(tag_id) for tag_id in self.request.GET['tags'].split(',')]
            for tag_id in tags:
                tags_str += Tag.objects.get(pk=tag_id).name
                tags_str += ','
            tags_str = tags_str[:len(tags_str) - 1]

        context = super(SearchView, self).get_context_data(**kwargs)
        context['people'] = people_str
        context['parties'] = parties_str
        context['tags'] = tags_str
        context['number_of_results'] = 3
        return context


class StatusFilterUnifiedView(ListView):
    model = Facebook_Status
    # paginate_by = 10
    context_object_name = 'filtered_statuses'

    def get_queryset(self):
        variable_column = self.kwargs['variable_column']
        search_string = self.kwargs['id']
        if self.kwargs['context_object'] == 'tag':
            search_field = self.kwargs['search_field']
            if search_field == 'id':
                search_field = 'id'
            else:
                search_field = 'name'
            selected_filter = variable_column + '__' + search_field
            try:
                query_set = Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by(
                    '-published')
            except FieldError:
                selected_filter = variable_column + '__' + 'name'
                query_set = Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by(
                    '-published')
                # TODO: Replace with redirect to actual url with 'name' in path, and HttpResponseRedirect()
            return query_set
        else:
            selected_filter = variable_column
            return Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')

    def get_context_data(self, **kwargs):
        context = super(StatusFilterUnifiedView, self).get_context_data(**kwargs)

        object_id = self.kwargs['id']
        search_field = self.kwargs.get('search_field', 'id')
        context['object'] = self.parent_model.objects.get(**{search_field: object_id})
        context['access_token'] = facebook.get_app_access_token(os.environ['FACEBOOK_APP_ID'], os.environ['FACEBOOK_SECRET_KEY'])
        return context


class PersonView(StatusFilterUnifiedView):
    template_name = "core/person.html"
    parent_model = Person


class PartyView(StatusFilterUnifiedView):
    template_name = "core/party.html"
    parent_model = Party


class TagView(StatusFilterUnifiedView):
    template_name = "core/tag.html"
    parent_model = Tag

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        context['side_bar_list'] = Person.objects.filter(
            facebook_feed__facebook_status__tags__id=context['object'].id).distinct()
        return context


class AllPersons(ListView):
    template_name = 'core/all_persons.html'
    model = Person


class AllParties(ListView):
    template_name = 'core/all_parties.html'
    model = Party


class AllTags(ListView):
    template_name = 'core/all_tags.html'
    model = Tag


def about_page(request):
    return render(request, 'core/about.html')


def add_tag(request, id):
    status = Facebook_Status.objects.get(id=id)
    tagsString = request.POST['tag']
    tagsList = tagsString.split(',')
    for tagName in tagsList:
        strippedTagName = tagName.strip()
        if strippedTagName:
            tag, created = Tag.objects.get_or_create(name=strippedTagName)
            if created:
                tag.name = strippedTagName
                tag.is_for_main_display = True
                tag.save()
                # add status to tag statuses
            tag.statuses.add(status)
            tag.save()

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # return HttpResponseRedirect(reverse('plain-index'))
    print request.META["HTTP_REFERER"]
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

# Views for getting facebook data using a user Token
def login_page(request):
    return render(request, 'core/login_page.html')


def get_data_from_facebook(request):
    user_access_token = request.POST['access_token']
    print user_access_token
    graph = facebook.GraphAPI(access_token=user_access_token)
    # graph.access_token = facebook.get_app_access_token(settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    stav = '508516607'
    anna = '509928464'
    a = graph.get_object(anna)
    print a
    # b = graph.request('https://graph.facebook.com/%s/statuses?access_token=%s' % (stav, user_access_token))
    # print b
    b = graph.get_connections(anna, 'statuses')
    print b

    return HttpResponseRedirect(request.META["HTTP_REFERER"])

#A handler for status_update ajax call from client
def status_update(request, status_id):

    status = Facebook_Status.objects.get(status_id=status_id)

    url = "https://graph.facebook.com/"
    url += str(status.status_id)
    url += "?access_token="+facebook.get_app_access_token(settings.FACEBOOK_APP_ID, settings.FACEBOOK_SECRET_KEY)
    url += "&fields=shares,likes.limit(1).summary(true),comments.limit(1).summary(true)"

    try:
        responseText = urllib2.urlopen(url).read()
        responseJson = json.loads(responseText)

        response_data = dict()
        response_data['likes'] = responseJson['likes']['summary']['total_count']
        response_data['comments'] = responseJson['comments']['summary']['total_count']
        response_data['shares'] = responseJson['shares']['count']
        response_data['id'] = status.status_id
        try:
            status.like_count = int(response_data['likes'])
            status.comment_count = int(response_data['comments'])
            status.share_count = int(response_data['shares'])
            status.save()
        finally:
            return HttpResponse(json.dumps(response_data), content_type="application/json")
    finally:
        response_data = dict()
        response_data['likes'] = status.like_count
        response_data['comments'] = status.comment_count
        response_data['shares'] = status.share_count
        response_data['id'] = status.status_id

        return HttpResponse(json.dumps(response_data), content_type="application/json")

#A handler for the search bar request from the client
def search_bar(request):
    searchText = request.GET['text']

    response_data = dict()
    response_data['number_of_results'] = 0
    response_data['results'] = []
    if searchText.strip() == "":
        print "NO STRING"
        return HttpResponse(json.dumps(response_data), content_type="application/json")

    people = Person.objects.filter(name__contains=searchText)
    for person in people:
        newResult = dict()
        newResult['id'] = person.id
        newResult['name'] = person.name
        newResult['party'] = person.party.name
        newResult['type'] = "PERSON"
        response_data['results'].append(newResult)
        response_data['number_of_results'] += 1

    tags = Tag.objects.filter(name__contains=searchText)
    for tag in tags:
        newResult = dict()
        newResult['id'] = tag.id
        newResult['name'] = tag.name
        newResult['type'] = "TAG"
        response_data['results'].append(newResult)
        response_data['number_of_results'] += 1

    parties = Party.objects.filter(name__contains=searchText)
    for party in parties:
        newResult = dict()
        newResult['id'] = party.id
        newResult['name'] = party.name
        newResult['type'] = "PARTY"
        response_data['results'].append(newResult)
        response_data['number_of_results'] += 1

    return HttpResponse(json.dumps(response_data), content_type="application/json")
