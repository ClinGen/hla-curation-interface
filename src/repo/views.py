"""Provides views for the repo app."""

from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView

from datatable.views import datatable
from repo.constants.views import PUBLISHED_CURATION_SEARCH_FIELDS
from repo.models import PublishedCuration
from repo.serializers import serialize_published_curation


def repo_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching published curations."""
    return datatable(
        request=request,
        model=PublishedCuration,
        order_by="-published_at",
        fields=PUBLISHED_CURATION_SEARCH_FIELDS,
        data_title="Published Curations",
        partial="repo/partials/search.html",
    )


class PublishedCurationDetail(DetailView):
    """Shows the user information about a published curation."""

    model = PublishedCuration
    template_name = "repo/detail.html"

    def get_object(self):
        """Get PublishedCuration by the curation's slug."""
        curation_slug = self.kwargs.get("curation_slug")
        return get_object_or_404(
            PublishedCuration,
            curation__slug=curation_slug,
        )

    def get_context_data(self, **kwargs):
        """Add curation to context for template convenience."""
        context = super().get_context_data(**kwargs)
        context["curation"] = self.object.curation
        return context


def download_all_json(request: HttpRequest) -> HttpResponse:
    """Downloads all published curations as JSON."""
    published_curations = PublishedCuration.objects.all().select_related(
        "curation__allele",
        "curation__haplotype",
        "curation__disease",
        "published_by",
    ).prefetch_related(
        "curation__evidence__publication",
        "curation__evidence__demographics",
    )

    data = {
        "published_curations": [
            serialize_published_curation(pc) for pc in published_curations
        ],
        "export_date": timezone.now().isoformat(),
        "total_count": published_curations.count(),
    }

    response = JsonResponse(data)
    response["Content-Disposition"] = (
        f'attachment; filename="hla_curations_{timezone.now().strftime("%Y%m%d")}.json"'
    )
    return response


def download_single_json(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Downloads a single published curation as JSON."""
    published = get_object_or_404(
        PublishedCuration.objects.select_related(
            "curation__allele",
            "curation__haplotype",
            "curation__disease",
            "published_by",
        ).prefetch_related(
            "curation__evidence__publication",
            "curation__evidence__demographics",
        ),
        curation__slug=curation_slug,
    )

    data = serialize_published_curation(published)

    response = JsonResponse(data)
    response["Content-Disposition"] = (
        f'attachment; filename="curation_{curation_slug}.json"'
    )
    return response
