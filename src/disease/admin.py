from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from disease.models import Disease


@admin.register(Disease)
class DiseaseAdmin(SimpleHistoryAdmin):
    list_display = ["name", "mondo_id", "disease_type"]
    list_filter = ["disease_type"]
    search_fields = ["name", "mondo_id"]
    readonly_fields = ["added_by", "added_at"]
