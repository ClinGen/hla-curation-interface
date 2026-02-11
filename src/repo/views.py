from typing import Any

from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.generic import DetailView, ListView

from repo.models import PublishedCuration
from repo.serializers import serialize_published_curation


class PublishedCurationList(ListView):
    model = PublishedCuration
    template_name = "repo/list.html"


class PublishedCurationDetail(DetailView):
    model = PublishedCuration
    template_name = "repo/detail.html"

    def get_object(self, _queryset: QuerySet[Any] | None = None) -> PublishedCuration:
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
            Context dictionary with curation added for template use.
        """
        context = super().get_context_data(**kwargs)
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
