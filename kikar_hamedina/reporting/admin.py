from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from reporting.models import WeeklyReportRecipients, RSSFeedKeyWord


class WeeklyReportRecipientInline(admin.StackedInline):
    model = WeeklyReportRecipients
    can_delete = False
    verbose_name = 'Weekly Report Recipient'
    verbose_name_plural = "Weekly Report Recipients"


class KeywordAdminTabularInline(admin.TabularInline):
    model = RSSFeedKeyWord
    extra = 1


class UserAdmin(UserAdmin):
    inlines = (WeeklyReportRecipientInline, KeywordAdminTabularInline)



admin.site.unregister(User)
admin.site.register(User, UserAdmin)