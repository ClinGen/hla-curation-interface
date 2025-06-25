"""Configures the admin site for the core app."""

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.http import HttpRequest

from core.models import UserProfile

# We customize the configuration for the User model.
admin.site.unregister(User)

# We don't use groups.
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Customizes the configuration for the User model in the admin site."""

    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002 (The request argument is expected.)
        """Returns false because we delegate adding to Firebase."""
        return False

    list_display = ["email", "username", "is_active", "is_staff"]
    list_display_links = ["email"]
    list_editable = ["is_active"]
    search_fields = ["username", "email"]
    list_filter = ["is_active", "is_staff", "is_superuser"]
    fieldsets = [
        (None, {"fields": ["username", "email", "is_active"]}),
        (
            "Permissions",
            {
                "fields": ["is_staff", "is_superuser"],
                "classes": ["collapse"],
            },
        ),
        (
            "Important Dates",
            {
                "fields": ["last_login", "date_joined"],
                "classes": ["collapse"],
            },
        ),
    ]
    readonly_fields = ["username", "email", "last_login", "date_joined"]


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Configures the UserProfile model in the admin site."""

    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002 (The request argument is expected.)
        """Returns false because we delegate adding to Firebase."""
        return False

    # We don't want admins to modify the Firebase fields of UserProfile objects because
    # Firebase should be the source of truth for users.
    readonly_fields = [
        "user",
        "firebase_uid",
        "firebase_email_verified",
        "firebase_photo_url",
        "firebase_display_name",
        "firebase_sign_in_provider",
    ]
