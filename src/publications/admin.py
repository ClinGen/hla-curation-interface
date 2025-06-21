"""Configures the admin site for the publications app."""

from django.contrib import admin

from publications.models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    """Configures the Publication model in the admin site."""

    list_display = ["title", "author", "publication_type", "doi"]
    list_filter = ["publication_type"]
    search_fields = ["title", "author", "doi"]
    readonly_fields = ["added_by", "added_at"]
