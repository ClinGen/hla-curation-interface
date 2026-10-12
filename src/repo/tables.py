import django_tables2 as tables
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import A

from repo.models import PublishedCuration


class PublishedCurationTable(tables.Table):
    slug = tables.LinkColumn(
        "repo-detail",
        kwargs={"curation_slug": A("curation__slug")},
        accessor="curation__slug",
        verbose_name="ID",
    )
    curation_type = tables.Column(
        accessor="curation__get_curation_type_display",
        verbose_name="Type",
        orderable=False,
    )
    allele = tables.Column(accessor="curation__allele", default="------")
    haplotype = tables.Column(accessor="curation__haplotype", default="------")
    disease = tables.Column(accessor="curation__disease", default="------")
    classification = tables.Column(
        accessor="curation__ep_classification",
        verbose_name="Classification",
        orderable=False,
        empty_values=(),
    )
    updated_at = tables.DateColumn(
        accessor="curation__updated_at",
        verbose_name="Updated",
        format="Y-m-d",
    )
    actions = tables.Column(empty_values=(), verbose_name="Actions", orderable=False)

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = (
            "slug",
            "curation_type",
            "allele",
            "haplotype",
            "disease",
            "classification",
            "updated_at",
            "actions",
        )

    def render_classification(self, record: PublishedCuration) -> str:
        return record.curation.classification_display

    def render_actions(self, record: PublishedCuration) -> str:
        url = reverse("repo-download-single", args=[record.curation.slug])
        icon = render_to_string("common/icon.html", {"icon_name": "download"})
        return format_html(
            '<a href="{}" class="button is-small is-link is-light">{}JSON</a>',
            url,
            icon,
        )
