"""Configures the admin site for the curation app."""

from django.contrib import admin

from curation.models import Curation


@admin.register(Curation)
class CurationAdmin(admin.ModelAdmin):
    """Configures the Curation model in the admin site."""

    list_display = ["pk", "curation_type", "added_by", "added_at"]
    list_filter = ["curation_type"]
    search_fields = []
    readonly_fields = ["added_by", "added_at"]
