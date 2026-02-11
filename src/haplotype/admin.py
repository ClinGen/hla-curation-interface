from django.contrib import admin

from haplotype.models import Haplotype


@admin.register(Haplotype)
class HaplotypeAdmin(admin.ModelAdmin):
    list_display = ["name", "added_by", "added_at"]
    search_fields = ["name"]
    readonly_fields = ["added_by", "added_at"]
