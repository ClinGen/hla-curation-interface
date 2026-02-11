from django.contrib import admin
from django.contrib.auth.models import Group

from auth_.models import UserProfile

# We don't use groups.
admin.site.unregister(Group)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "has_curation_permissions", "has_signed_phi_agreement"]
