from django import template


register = template.Library()


@register.filter(name='proper_tag')
def set_proper_tag(tag):
    if tag.synonym_synonym_tag.exists():
        # if is a synonym of another tag, redirect
        proper_tag = tag.synonym_synonym_tag.first().tag
        return proper_tag
    else:
        return tag