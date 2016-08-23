# -*- coding: utf-8 -*-
from django.contrib import admin

from kikartags.models import Tag
from kikartags.models import TaggedItem, TagSynonym


class TaggedItemInline(admin.TabularInline):
    model = TaggedItem
    extra = 1
    max_num = 5


class TagSynonymInline(admin.TabularInline):
    model = TagSynonym
    extra = 1
    fk_name = 'proper_form_of_tag'


class TagAdmin(admin.ModelAdmin):
    inlines = (TagSynonymInline, TaggedItemInline)

admin.site.register(Tag, TagAdmin)
admin.site.register(TaggedItem)
