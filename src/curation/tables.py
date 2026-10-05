import django_tables2 as tables
from django.template.loader import render_to_string
from django_tables2 import A

from curation.constants.models.common import Status
from curation.models import Curation

# The common tag template for each curation status.
STATUS_TAGS = {
    Status.IN_PROGRESS: "common/tags/in_progress.html",
    Status.PROVISIONAL: "common/tags/provisional.html",
    Status.APPROVED: "common/tags/approved.html",
    Status.PUBLISHED: "common/tags/published.html",
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
        empty_values=(),
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
        return render_to_string(STATUS_TAGS[record.status])

    def render_classification(self, record: Curation) -> str:
        return record.classification_display
