from django.contrib import admin
from django.contrib.contenttypes import generic

from models import ElectedKnesset, Candidate, CandidateList, Party, CandidateListAltname
from links.models import Link
from facebook_feeds.admin import Facebook_FeedAdminInline, Facebook_PersonaAdminInline


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


class PartyAdminInline(admin.TabularInline):
    model = Party
    extra = 1


class CandidateAdminInline(admin.TabularInline):
    model = Candidate
    extra = 1


class CandidateListAdmin(admin.ModelAdmin):
    inlines = [CandidateListAltnameInline, CandidateAdminInline]

admin.site.register(CandidateList, CandidateListAdmin)




class CandidateAdmin(admin.ModelAdmin):
    inlines = [LinksInline, ]


admin.site.register(Candidate, CandidateAdmin)

admin.site.register(ElectedKnesset)