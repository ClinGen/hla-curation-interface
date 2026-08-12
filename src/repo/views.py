from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from curation.models import Curation

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView
from django_tables2 import RequestConfig

from common.history import resolve_changes
from common.tables import HistoryTable
from common.views import SearchListView
from curation.constants.models.common import Status
from repo.models import PublishedCuration
from repo.serializers import serialize_published_curation
from repo.tables import PublishedCurationTable


def is_superseded(published_curation: PublishedCuration) -> bool:
    """Returns True if a direct or transitive copy is also published."""

    def _has_published_copy(curation: "Curation") -> bool:
        for copy in curation.copies.all():  # type: ignore
            if copy.status == Status.PUBLISHED:
                return True
            if _has_published_copy(copy):
                return True
        return False

    return _has_published_copy(published_curation.curation)


def get_superseding(published_curation: PublishedCuration) -> PublishedCuration | None:
    """Returns the most recently published descendant, or None if not superseded."""

    def _find_latest(curation: "Curation") -> PublishedCuration | None:
        result = None
        for copy in curation.copies.all():  # type: ignore
            if copy.status == Status.PUBLISHED:
                candidate = copy.publication
                if result is None or candidate.published_at > result.published_at:
                    result = candidate
            deeper = _find_latest(copy)
            if deeper is not None and (
                result is None or deeper.published_at > result.published_at
            ):
                result = deeper
        return result

    return _find_latest(published_curation.curation)


class PublishedCurationList(SearchListView):
    model = PublishedCuration
    template_name = "repo/list.html"
    ordering = ["-curation__updated_at"]
    table_class = PublishedCurationTable
    search_fields = [
        "curation__slug",
        "curation__allele__name",
        "curation__haplotype__name",
        "curation__disease__name",
    ]
    table_pagination = {"per_page": 25}


class PublishedCurationDetail(DetailView):
    model = PublishedCuration
    template_name = "repo/detail.html"

    def get_object(self, queryset: QuerySet[Any] | None = None) -> PublishedCuration:  # noqa: ARG002
        """Get PublishedCuration by the curation's slug.

        Returns:
            PublishedCuration instance matching the slug from URL kwargs.
        """
        curation_slug = self.kwargs.get("curation_slug")
        return get_object_or_404(
            PublishedCuration,
            curation__slug=curation_slug,
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        """Add curation to context for template convenience.

        Returns:
            Context dict with curation, superseded, and superseding keys added.
        """
        context = super().get_context_data(**kwargs)
        context["curation"] = self.object.curation
        context["superseded"] = is_superseded(self.object)
        context["superseding"] = get_superseding(self.object)
        return context


class PublishedCurationHistory(DetailView):
    model = PublishedCuration
    template_name = "repo/history.html"

    def get_object(self, queryset: QuerySet[Any] | None = None) -> PublishedCuration:  # noqa: ARG002
        return get_object_or_404(
            PublishedCuration, curation__slug=self.kwargs["curation_slug"]
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        history_table = HistoryTable(
            self.object.history.all(),
            change_url_name="repo-change",
            change_url_slug1=self.object.curation.slug,
        )
        RequestConfig(self.request).configure(history_table)
        context["history_table"] = history_table
        context["curation"] = self.object.curation
        return context


class PublishedCurationChange(DetailView):
    model = PublishedCuration
    template_name = "repo/change.html"

    def get_object(self, queryset: QuerySet[Any] | None = None) -> PublishedCuration:  # noqa: ARG002
        return get_object_or_404(
            PublishedCuration, curation__slug=self.kwargs["curation_slug"]
        )

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        record = self.object.history.get(history_id=self.kwargs["history_id"])
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(PublishedCuration, record, prev_record)
        context["curation"] = self.object.curation
        return context


def download_all_json(request: HttpRequest) -> HttpResponse:
    """Downloads all published curations as JSON.

    Returns:
        JSON response with all published curations and metadata.
    """
    published_curations = PublishedCuration.objects.all()
    timestamp = timezone.now().strftime("%Y-%m-%d")
    data = {
        "published_curations": [
            serialize_published_curation(pc) for pc in PublishedCuration.objects.all()
        ],
        "total_count": published_curations.count(),
        "export_date": timestamp,
    }
    response = JsonResponse(data)
    response["Content-Disposition"] = (
        f'attachment; filename="hla_curations_all_{timestamp}.json"'
    )
    return response


def download_single_json(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Downloads a single published curation as JSON.

    Returns:
        JSON response with the specified published curation.
    """
    published = get_object_or_404(PublishedCuration, curation__slug=curation_slug)
    timestamp = timezone.now().strftime("%Y-%m-%d")
    data = {
        "curation": serialize_published_curation(published),
        "export_date": timestamp,
    }
    response = JsonResponse(data)
    response["Content-Disposition"] = (
        f'attachment; filename="hla_curation_{curation_slug}.json"'
    )
    return response
