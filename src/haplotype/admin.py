"""Configures the admin site for the haplotype app."""

from django.contrib import admin

from haplotype.models import Haplotype


@admin.register(Haplotype)
class HaplotypeAdmin(admin.ModelAdmin):
    """Configures the Haplotype model in the admin site."""

    list_display = ["name", "car_id", "added_by", "added_at"]
    search_fields = ["name", "car_id"]
    readonly_fields = ["added_by", "added_at"]
