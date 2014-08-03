from urllib2 import unquote
from django import template
from django.template.defaultfilters import floatformat


register = template.Library()


@register.filter(name='link')
def link(status):
    """Returns the post link for a status"""
    return 'https://www.facebook.com/%s/posts/%s' % (status.status_id.split('_')[0], status.status_id.split('_')[1])


@register.filter(name='embed_link')
def link(status):
    """Returns the embed link for a post"""
    return '%s/posts/%s' % (status.feed.link, status.status_id.split('_')[1])


@register.filter(name='percent')
def percent(value):
    print 'value:', value, type(value)
    if value is None:
        return None
    return floatformat(value * 100.0, 2) + '%'


@register.filter(name='urldecode')
def unquote_new(value):
    return unquote(value).decode()