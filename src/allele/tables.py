import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from allele.models import Allele


class AlleleTable(tables.Table):
    slug = tables.LinkColumn("allele-detail", args=[A("slug")], verbose_name="ID")
    name = tables.Column()
    car_id = tables.Column(verbose_name="CAR ID", orderable=False)
    updated_at = tables.DateColumn(verbose_name="Updated", format="Y-m-d")

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = ("slug", "name", "car_id", "updated_at")

    def render_car_id(self, value: str | None, record: Allele) -> str:  # noqa: ARG002
        if value:
            url = f"https://reg.clinicalgenome.org/allele/ui/hla/id/{value}"
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">'
                "{} "
                '<i class="bi bi-box-arrow-up-right"></i>'
                "</a>",
                url,
                value,
            )
        return "------"
