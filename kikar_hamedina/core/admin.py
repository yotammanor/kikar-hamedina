from django.contrib import admin
from models import Party, Person, Facebook_Feed, Facebook_Status, Tag, User_Token, Feed_Popularity

admin.site.register(Party)
admin.site.register(Person)
admin.site.register(Facebook_Feed)
admin.site.register(Facebook_Status)
admin.site.register(Tag)
admin.site.register(User_Token)
admin.site.register(Feed_Popularity)
