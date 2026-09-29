import django_tables2 as tables
from django.utils.html import format_html
from django_tables2 import A

from curation.constants.models.common import Status
from curation.constants.models.curation import CLASSIFICATION_CHOICES
from curation.models import Curation

# The tag color, Bootstrap icon, and label for each curation status.
STATUS_TAGS = {
    Status.IN_PROGRESS: ("is-warning", "bi-cone-striped", "In Progress"),
    Status.PROVISIONAL: ("is-danger", "bi-hourglass-split", "Provisional"),
    Status.APPROVED: ("is-info", "bi-check-circle", "Approved"),
    Status.PUBLISHED: ("is-info is-light", "bi-book", "Published"),
}


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

    def render_status(self, value: str, record: Curation) -> str:
        # django-tables2 passes the choice label as value, so key on the code.
        if record.status not in STATUS_TAGS:
            return value
        color, icon, label = STATUS_TAGS[record.status]
        return format_html(
            '<span class="tag {}"><i class="bi {}"></i> {}</span>', color, icon, label
        )

    def render_classification(self, value: str | None, record: Curation) -> str:
        if value:
            return record.get_ep_classification_display()  # type: ignore
        sc = record.suggested_classification
        if sc:
            return CLASSIFICATION_CHOICES.get(sc, "------")
        return "------"
