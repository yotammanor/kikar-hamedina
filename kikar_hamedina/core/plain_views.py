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


# class PersonView(ListView):
#     model = Facebook_Status
#     paginate_by = 10
#
#     def get_queryset(self):
#         return Facebook_Status.objects.filter(feed__person__id=self.kwargs['id']).order_by('-published')
#
#
# class PartyView(ListView):
#     model = Facebook_Status
#     paginate_by = 10
#
#     def get_queryset(self):
#         return Facebook_Status.objects.filter(feed__person__party__id=self.kwargs['id']).order_by('-published')
#
#
# class TagView(ListView):
#     model = Facebook_Status
#     paginate_by = 10
#
#     def get_queryset(self):
#         return Facebook_Status.objects.filter(tags__id=self.kwargs['id']).order_by('-published')


class StatusIdFilterView(ListView):
    model = Facebook_Status
    paginate_by = 10
    # context_object_name = 'filtered_statuses'

    def get_queryset(self):
        variable_column = self.kwargs['variable_column']
        # search_field = 'id'
        search_string = self.kwargs['id']
        selected_filter = variable_column
        return Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')

    # def get_context_data(self, **kwargs):



class StatusFilterView(ListView):
    model = Facebook_Status
    paginate_by = 10

    def get_queryset(self):
        variable_column = self.kwargs['variable_column']
        search_field = self.kwargs['search_field']
        search_string = self.kwargs['id']
        selected_filter = variable_column + '__' + search_field
        try:
            query_set = Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')
        except FieldError:
            selected_filter = variable_column + '__' + 'name'
            query_set = Facebook_Status.objects.filter(**{selected_filter: search_string}).order_by('-published')
            # TODO: Replace with redirect to actual url with 'name' in path, and HttpResponseRedirect()
        return query_set


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