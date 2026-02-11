from django.contrib import admin

from publication.models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ["title", "author", "publication_type", "doi"]
    list_filter = ["publication_type"]
    search_fields = ["title", "author", "doi"]
    readonly_fields = ["added_by", "added_at"]
