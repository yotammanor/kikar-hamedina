from django.contrib import admin
from models import Person, PersonAltname, Title, Role


class RoleInline(admin.TabularInline):
    model = Role


class PersonAltnameInline(admin.TabularInline):
    model = PersonAltname
    extra = 1


class PersonAdmin(admin.ModelAdmin):
    ordering = ('name',)
    inlines = [
        RoleInline,
        PersonAltnameInline,
    ]

admin.site.register(Person, PersonAdmin)



class TitleAdmin(admin.ModelAdmin):
    ordering = ('name',)


admin.site.register(Title, TitleAdmin)


class RoleAdmin(admin.ModelAdmin):
    ordering = ('person',)
    list_display = ('person', 'text')


admin.site.register(Role, RoleAdmin)
