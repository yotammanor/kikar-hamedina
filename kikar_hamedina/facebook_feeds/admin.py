from django.contrib import admin

from models import Facebook_Feed, \
    Facebook_Status, \
    Tag as OldTag, \
    User_Token, Feed_Popularity, Facebook_Persona, \
    Facebook_Status_Attachment, Status_Comment_Pattern


admin.site.register(Facebook_Feed)
admin.site.register(Facebook_Status)
admin.site.register(OldTag)
admin.site.register(User_Token)
admin.site.register(Feed_Popularity)
admin.site.register(Facebook_Status_Attachment)
admin.site.register(Status_Comment_Pattern)
