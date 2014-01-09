from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.template.defaultfilters import slugify
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag

class HomeView(ListView):
  model = Facebook_Status
  paginate_by = 10

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
                name = strippedTagName,
                slug = slugify(strippedTagName)
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