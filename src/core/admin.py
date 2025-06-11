"""Configures the admin site for the core app."""

from django.contrib import admin
from django.contrib.auth.models import Group, User

from core.models import UserProfile

# We don't want admins to modify User objects because Firebase should be the source of
# truth for users.
admin.site.unregister(User)

# We don't use groups.
admin.site.unregister(Group)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Configures the UserProfile model in the admin site."""

    # We don't want admins to modify the Firebase fields of UserProfile objects because
    # Firebase should be the source of truth for users.
    readonly_fields = (
        "user",
        "firebase_uid",
        "firebase_email_verified",
        "firebase_photo_url",
        "firebase_display_name",
    )
