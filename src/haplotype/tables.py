import django_tables2 as tables
from django_tables2 import A

from haplotype.models import Haplotype


class HaplotypeTable(tables.Table):
    slug = tables.LinkColumn("haplotype-detail", args=[A("slug")], verbose_name="ID")
    name = tables.Column()
    updated_at = tables.DateColumn(verbose_name="Updated", format="Y-m-d")

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = ("slug", "name", "updated_at")

    def render_name(self, value: str, record: Haplotype) -> str:  # ruff: ignore[unused-method-argument]
        return record.display_name
