from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from reporting.models import WeeklyReportRecipients


class WeeklyReportRecipientInline(admin.StackedInline):
    model = WeeklyReportRecipients
    can_delete = False
    verbose_name = 'Weekly Report Recipient'
    verbose_name_plural = "Weekly Report Recipients"


class UserAdmin(UserAdmin):
    inlines = (WeeklyReportRecipientInline,)


admin.site.unregister(User)
admin.site.register(User, UserAdmin)