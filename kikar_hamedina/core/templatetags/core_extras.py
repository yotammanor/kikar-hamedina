from django import template

register = template.Library()

@register.filter(name='link')
def link(status):
    """Returns the post link for a status"""
    return 'https://www.facebook.com/%s/posts/%s'%(status.status_id.split('_')[0], status.status_id.split('_')[1])