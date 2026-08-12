import django_tables2 as tables
from django.urls import reverse
from django.utils.html import format_html
from django_tables2 import A

from curation.constants.models.curation import CLASSIFICATION_CHOICES
from repo.models import PublishedCuration


class PublishedCurationTable(tables.Table):
    slug = tables.LinkColumn(
        "repo-detail",
        kwargs={"curation_slug": A("curation.slug")},
        accessor="curation.slug",
        verbose_name="ID",
    )
    curation_type = tables.Column(
        accessor="curation.get_curation_type_display",
        verbose_name="Type",
        orderable=False,
    )
    allele = tables.Column(accessor="curation.allele", default="------")
    haplotype = tables.Column(accessor="curation.haplotype", default="------")
    disease = tables.Column(accessor="curation.disease", default="------")
    classification = tables.Column(
        accessor="curation.ep_classification",
        verbose_name="Classification",
        orderable=False,
    )
    updated_at = tables.DateColumn(
        accessor="curation.updated_at",
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

    def render_classification(
        self, value: str | None, record: PublishedCuration
    ) -> str:
        if value:
            return record.curation.get_ep_classification_display()
        sc = record.curation.suggested_classification
        if sc:
            return CLASSIFICATION_CHOICES.get(sc, "------")
        return "------"

    def render_actions(self, record: PublishedCuration) -> str:
        url = reverse("repo-download-single", args=[record.curation.slug])
        return format_html(
            '<a href="{}" class="button is-small">'
            '<i class="bi bi-download"></i> JSON'
            "</a>",
            url,
        )
