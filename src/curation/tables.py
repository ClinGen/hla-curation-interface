import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from curation.constants.models.common import Status
from curation.constants.models.curation import CLASSIFICATION_CHOICES
from curation.models import Curation


class CurationTable(tables.Table):
    slug = tables.LinkColumn(
        "curation-detail",
        kwargs={"curation_slug": A("slug")},
        verbose_name="ID",
    )
    curation_type = tables.Column(
        accessor="get_curation_type_display",
        verbose_name="Type",
        orderable=False,
    )
    allele = tables.Column(default="------")
    haplotype = tables.Column(default="------")
    disease = tables.Column(default="------")
    status = tables.Column(orderable=False)
    classification = tables.Column(
        accessor="ep_classification",
        verbose_name="Classification",
        orderable=False,
    )
    updated_at = tables.DateColumn(verbose_name="Updated", format="Y-m-d")

    class Meta:
        attrs = {"class": "table is-fullwidth is-hoverable"}
        sequence = (
            "slug",
            "curation_type",
            "allele",
            "haplotype",
            "disease",
            "status",
            "classification",
            "updated_at",
        )

    def render_status(self, value: str, record: Curation) -> str:  # noqa: ARG002
        if value == Status.IN_PROGRESS:
            return format_html(
                '<span class="tag is-warning">'
                '<i class="bi bi-cone-striped"></i> In Progress'
                "</span>"
            )
        if value == Status.READY_FOR_REVIEW:
            return format_html(
                '<span class="tag is-danger">'
                '<i class="bi bi-flag-fill"></i> Needs Review'
                "</span>"
            )
        if value == Status.PROVISIONAL:
            return format_html(
                '<span class="tag is-info">'
                '<i class="bi bi-hourglass-split"></i> Provisional'
                "</span>"
            )
        if value == Status.PUBLISHED:
            return format_html(
                '<span class="tag is-info is-light">'
                '<i class="bi bi-book"></i> Published'
                "</span>"
            )
        return value

    def render_classification(self, value: str | None, record: Curation) -> str:
        if value:
            return record.get_ep_classification_display()  # type: ignore
        sc = record.suggested_classification
        if sc:
            return CLASSIFICATION_CHOICES.get(sc, "------")
        return "------"
