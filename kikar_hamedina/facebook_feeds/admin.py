from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Facebook_Feed, \
    Facebook_Status, \
    Tag as OldTag, \
    User_Token, Feed_Popularity, Facebook_Persona, \
    Facebook_Status_Attachment, Status_Comment_Pattern


class Facebook_PersonaAdminInline(generic.GenericTabularInline):
    model = Facebook_Persona
    extra = 1


class Facebook_FeedAdminInline(admin.TabularInline):
    model = Facebook_Feed
    fields = ('id', 'vendor_id', 'username',)


class Facebook_StatusAdmin(admin.ModelAdmin):
    model = Facebook_Status

    def mk_name(self, obj):
        if obj.feed.persona.content_object:
            return obj.feed.persona.content_object.name
        return None

    def mk_id(self, obj):
        if obj.feed.persona.content_object:
            return obj.feed.persona.content_object.id
        return None

    def truncated_content(self, obj):
        return obj.content[:50]

    list_display = (
        'id', 'status_id', 'truncated_content', 'feed', 'mk_name', 'mk_id', 'published', 'is_comment',
        'publication_restricted', 'is_deleted')
    list_editable = ('publication_restricted', 'is_deleted')
    search_fields = ('id', 'status_id', 'content')
    list_filter = ('publication_restricted',)


admin.site.register(Facebook_Feed)
admin.site.register(Facebook_Status, Facebook_StatusAdmin)
admin.site.register(OldTag)
admin.site.register(User_Token)
admin.site.register(Feed_Popularity)
admin.site.register(Facebook_Persona)
admin.site.register(Facebook_Status_Attachment)
admin.site.register(Status_Comment_Pattern)
