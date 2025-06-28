"""Configures the admin site for the allele app."""

from django.contrib import admin

from allele.models import Allele


@admin.register(Allele)
class AlleleAdmin(admin.ModelAdmin):
    """Configures the Allele model in the admin site."""

    list_display = ["name", "car_id", "added_by", "added_at"]
    search_fields = ["car_id"]
    readonly_fields = ["added_by", "added_at"]
