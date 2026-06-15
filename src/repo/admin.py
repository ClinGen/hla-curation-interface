from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from repo.models import PublishedCuration


@admin.register(PublishedCuration)
class PublishedCurationAdmin(SimpleHistoryAdmin):
    list_display = ["curation", "published_by", "published_at", "version"]
    readonly_fields = ["published_by", "published_at"]
