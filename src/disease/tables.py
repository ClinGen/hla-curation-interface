import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from disease.models import Disease


class DiseaseTable(tables.Table):
    slug = tables.LinkColumn("disease-detail", args=[A("slug")], verbose_name="ID")
    name = tables.Column()
    mondo_id = tables.Column(verbose_name="Mondo ID", orderable=False)
    updated_at = tables.DateColumn(verbose_name="Updated", format="Y-m-d")

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = ("slug", "name", "mondo_id", "updated_at")

    def render_mondo_id(self, value: str, record: Disease) -> str:
        if record.iri and value:
            return format_html(
                '<a href="{}" target="_blank" rel="noopener noreferrer">'
                "{} "
                '<i class="bi bi-box-arrow-up-right"></i>'
                "</a>",
                record.iri,
                value,
            )
        return "------"
