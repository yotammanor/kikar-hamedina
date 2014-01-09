import unicodedata
import re
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.views.generic.list import ListView
from django.utils.safestring import mark_safe
from django.template.defaultfilters import slugify
from .models import Facebook_Status, Facebook_Feed, Person, Party, Tag

from django.template import defaultfilters


# @defaultfilters.stringfilter
# @defaultfilters.register.filter(is_safe=True)
def unicode_slugify(value):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    try:
        value.encode('ascii')
        return slugify(value)

    except UnicodeDecodeError or UnicodeEncodeError:
        # value = unicode(value)
        value = re.sub('[\"\'&<>\{}]', '', value).strip()
        value = re.sub('[-\s]+', '-', value)
        # value = value.encode(encoding='unicode')
        return value


class HomeView(ListView):
    model = Facebook_Status
    paginate_by = 10


def add_tag(request, id):
    status = Facebook_Status.objects.get(id=id)
    print 'here1'
    print type(request.POST['tag'])
    print request.POST['tag'].encode('utf-8')
    slug = unicode_slugify(request.POST['tag'].encode('utf-8'))
    print 'there'
    print type(slug)
    try:
        tag = Tag.objects.get(name=request.POST['tag'])
    except Tag.DoesNotExist:
        # create tag
        tag = Tag(
            name=request.POST['tag'],
            slug=slug
        )
        print tag.slug
        tag.save()
    finally:
        print "here2"
        # add status to tag statuses
        tag.statuses.add(status)
        tag.save()

    # Always return an HttpResponseRedirect after successfully dealing
    # with POST data. This prevents data from being posted twice if a
    # user hits the Back button.
    # return HttpResponseRedirect(reverse('plain-index'))
    print request.META["HTTP_REFERER"]
    return HttpResponseRedirect(request.META["HTTP_REFERER"])