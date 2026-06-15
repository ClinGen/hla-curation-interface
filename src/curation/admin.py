from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from curation.models import Curation, Demographic, Evidence


@admin.register(Curation)
class CurationAdmin(SimpleHistoryAdmin):
    list_display = [
        "pk",
        "curation_type",
        "allele",
        "haplotype",
        "added_by",
        "added_at",
    ]
    list_filter = ["curation_type"]
    search_fields = ["allele", "haplotype"]
    readonly_fields = ["added_by", "added_at"]


@admin.register(Demographic)
class DemographicAdmin(SimpleHistoryAdmin):
    list_display = ["group"]
    search_fields = ["group"]


@admin.register(Evidence)
class EvidenceAdmin(SimpleHistoryAdmin):
    list_display = [
        "pk",
        "curation",
        "publication",
        "status",
        "added_at",
    ]
    list_filter = ["status"]
    search_fields = ["publication"]
    readonly_fields = ["added_by", "added_at"]
