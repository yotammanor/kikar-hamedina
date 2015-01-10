from django.contrib import admin
from django.contrib.contenttypes import generic

from models import Candidate, CandidateList, Party, CandidateAltname, CandidateListAltname
from links.models import Link


class CandidateAltnameInline(admin.TabularInline):
    model = CandidateAltname
    extra = 1

class CandidateListAltnameInline(admin.TabularInline):
    model = CandidateListAltname
    extra = 1

class MembershipInline(admin.TabularInline):
    model = CandidateList.candidates.through
    extra = 1

class LinksInline(generic.GenericTabularInline):
    model = Link
    ct_fk_field = 'object_pk'
    extra = 1

class CandidateListAdmin(admin.ModelAdmin):
    inlines = [LinksInline, CandidateListAltnameInline]

admin.site.register(CandidateList, CandidateListAdmin)

class CandidateAdmin(admin.ModelAdmin):
    inlines = [LinksInline, CandidateAltnameInline]


admin.site.register(Candidate, CandidateAdmin)


class PartyAdmin(admin.ModelAdmin):
    pass


admin.site.register(Party, PartyAdmin)
