from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from publication.models import Publication


@admin.register(Publication)
class PublicationAdmin(SimpleHistoryAdmin):
    list_display = ["title", "author", "publication_type", "doi"]
    list_filter = ["publication_type"]
    search_fields = ["title", "author", "doi"]
    readonly_fields = ["added_by", "added_at"]
