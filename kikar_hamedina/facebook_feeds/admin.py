from django.contrib import admin

from models import Facebook_Feed, \
    Facebook_Status, \
    Tag, \
    User_Token, Feed_Popularity, Facebook_Feed_Generic, \
    Facebook_Status_Attachment, Facebook_Status_Attachment_Media


admin.site.register(Facebook_Feed)
admin.site.register(Facebook_Status)
admin.site.register(Tag)
admin.site.register(User_Token)
admin.site.register(Feed_Popularity)
admin.site.register(Facebook_Status_Attachment)
admin.site.register(Facebook_Status_Attachment_Media)
