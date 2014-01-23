from django.core.exceptions import FieldError
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.template.defaultfilters import slugify
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag


class HomeView(ListView):
    model = Facebook_Status
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)
        context['navPersons'] = Person.objects.all().order_by('name')
        context['navParties'] = Party.objects.all().order_by('name')
        context['navTags'] = Tag.objects.all().order_by('name')
        context['context_object'] = self.kwargs['context_object']
        return context


class StatusFilterUnifiedView(ListView):
    model = Facebook_Status
    paginate_by = 10
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
            print selected_filter, search_string
            try:
                query_set = Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')
                print query_set
            except FieldError:
                selected_filter = variable_column + '__' + 'name'
                query_set = Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')
                # TODO: Replace with redirect to actual url with 'name' in path, and HttpResponseRedirect()
            return query_set
        else:
            selected_filter = variable_column
            return Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')

    def get_context_data(self, **kwargs):
        context = super(StatusFilterUnifiedView, self).get_context_data(**kwargs)
        context['navPersons'] = Person.objects.all().order_by('name')
        context['navParties'] = Party.objects.all().order_by('name')
        context['navTags'] = Tag.objects.all().order_by('name')
        context['context_object'] = self.kwargs['context_object']

        object_id = self.kwargs['id']
        if context['context_object'] == 'party':
            context['party'] = Party.objects.get(id=object_id)
            context['number_of_people_in_party'] = Person.objects.filter(party__id=object_id).count()

        elif context['context_object'] == 'person':
            context['person'] = Person.objects.get(id=object_id)

        elif context['context_object'] == 'tag':
            if self.kwargs['search_field'] == 'id':
                context['tag'] = Tag.objects.get(id=object_id)
            else:
                context['tag'] = Tag.objects.get(name=object_id)
        elif context['context_object'] == 'index':
            pass

        return context


def add_tag(request, id):
    status = Facebook_Status.objects.get(id=id)

    tagsString = request.POST['tag']
    tagsList = tagsString.split(',')

    for tagName in tagsList:
        strippedTagName = tagName.strip()
        try:
            tag = Tag.objects.get(name=strippedTagName)
        except Tag.DoesNotExist:
            # create tag
            tag = Tag(
                name=strippedTagName,
                slug=slugify(strippedTagName)
            )
            tag.save()
        finally:
            # add status to tag statuses
            tag.statuses.add(status)
            tag.save()

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # return HttpResponseRedirect(reverse('plain-index'))
    print request.META["HTTP_REFERER"]
    return HttpResponseRedirect(request.META["HTTP_REFERER"])