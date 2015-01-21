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

admin.site.register(Facebook_Feed)
admin.site.register(Facebook_Status)
admin.site.register(OldTag)
admin.site.register(User_Token)
admin.site.register(Feed_Popularity)
admin.site.register(Facebook_Persona)
admin.site.register(Facebook_Status_Attachment)
admin.site.register(Status_Comment_Pattern)
