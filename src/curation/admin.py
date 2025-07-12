"""Configures the admin site for the curation app."""

from django.contrib import admin

from curation.models import Curation, Evidence


@admin.register(Curation)
class CurationAdmin(admin.ModelAdmin):
    """Configures the Curation model in the admin site."""

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


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    """Configures the Curation model in the admin site."""

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
