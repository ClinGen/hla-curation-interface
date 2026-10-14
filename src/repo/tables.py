import django_tables2 as tables
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html, format_html_join
from django_tables2 import A

from repo.models import PublishedCuration

# The download buttons in each row: URL name, icon, and label.
DOWNLOAD_BUTTONS = (
    ("repo-download-single", "download", "JSON"),
    ("repo-download-single-csv", "filetype-csv", "CSV"),
    ("repo-download-single-xlsx", "file-earmark-spreadsheet", "Excel"),
)


class PublishedCurationTable(tables.Table):
    slug = tables.LinkColumn(
        "repo-detail",
        kwargs={"curation_slug": A("curation__slug")},
        accessor="curation__slug",
        verbose_name="ID",
    )
    allele = tables.Column(accessor="curation__allele", default="------")
    haplotype = tables.Column(accessor="curation__haplotype", default="------")
    disease = tables.Column(accessor="curation__disease", default="------")
    classification = tables.Column(
        accessor="curation__taskforce_classification",
        verbose_name="Classification",
        orderable=False,
        empty_values=(),
    )
    published_at = tables.DateColumn(verbose_name="Published", format="Y-m-d")
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = (
            "slug",
            "allele",
            "haplotype",
            "disease",
            "classification",
            "published_at",
            "actions",
        )

    def render_classification(self, record: PublishedCuration) -> str:
        return record.curation.classification_display

    def render_actions(self, record: PublishedCuration) -> str:
        slug = record.curation.slug
        links = (
            (
                reverse(url_name, args=[slug]),
                render_to_string("common/icon.html", {"icon_name": icon}),
                label,
            )
            for url_name, icon, label in DOWNLOAD_BUTTONS
        )
        return format_html(
            '<div class="buttons is-flex-wrap-nowrap">{}</div>',
            format_html_join(
                "",
                '<a href="{}" class="button is-small is-link is-light">{}{}</a>',
                links,
            ),
        )
