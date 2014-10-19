from django.contrib import admin

from kikartags.models import Tag, TaggedItem, TagSynonym


admin.site.register(Tag)
admin.site.register(TaggedItem)
admin.site.register(TagSynonym)

