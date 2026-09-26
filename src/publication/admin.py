from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from publication.models import Publication


@admin.register(Publication)
class PublicationAdmin(SimpleHistoryAdmin):
    list_display = ["title", "author", "pubmed_id"]
    search_fields = ["title", "author", "pubmed_id"]
    readonly_fields = ["added_by", "added_at"]
