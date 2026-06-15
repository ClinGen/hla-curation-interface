from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from allele.models import Allele


@admin.register(Allele)
class AlleleAdmin(SimpleHistoryAdmin):
    list_display = ["name", "car_id", "added_by", "added_at"]
    search_fields = ["car_id"]
    readonly_fields = ["added_by", "added_at"]
