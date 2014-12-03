from django import template
from kikartags.models import Tag

register = template.Library()


@register.filter(name='proper_tag')
def get_proper_tag(tag):
    return Tag.objects.get_proper(id=tag.id)