from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from haplotype.models import Haplotype


@admin.register(Haplotype)
class HaplotypeAdmin(SimpleHistoryAdmin):
    list_display = ["name", "added_by", "added_at"]
    search_fields = ["name"]
    readonly_fields = ["added_by", "added_at"]
