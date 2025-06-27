"""Configures the admin site for the disease app."""

from django.contrib import admin

from disease.models import Disease


@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    """Configures the Disease model in the admin site."""

    list_display = ["name", "mondo_id", "disease_type"]
    list_filter = ["disease_type"]
    search_fields = ["name", "mondo_id"]
    readonly_fields = ["added_by", "added_at"]
