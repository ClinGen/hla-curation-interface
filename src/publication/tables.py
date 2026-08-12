import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from publication.models import Publication


class PublicationTable(tables.Table):
    slug = tables.LinkColumn("publication-detail", args=[A("slug")], verbose_name="ID")
    title = tables.Column()
    author = tables.Column()
    publication_year = tables.Column(verbose_name="Year")
    pubmed_id = tables.Column(verbose_name="PMID")
    doi = tables.Column(verbose_name="DOI")
    updated_at = tables.DateColumn(verbose_name="Updated", format="Y-m-d")

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = (
            "slug",
            "title",
            "author",
            "publication_year",
            "pubmed_id",
            "doi",
            "updated_at",
        )

    def render_title(self, value: str, record: Publication) -> str:  # noqa: ARG002
        return format_html("<i>{}</i>", value)
