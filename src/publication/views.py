from typing import cast

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django_tables2 import RequestConfig

from auth_.permissions import ProtectedViewMixin, protected_view
from common.history import resolve_changes
from common.tables import HistoryTable
from common.views import SearchListView
from publication.clients import refresh_from_pubmed
from publication.forms import PublicationForm
from publication.models import Publication
from publication.tables import PublicationTable

REFRESH_FAILED_MESSAGE = (
    "Unable to refresh this publication from PubMed. Please try again later."
)


class PublicationCreate(ProtectedViewMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = "publication/create.html"
    success_url = reverse_lazy("publication-list")

    def form_valid(self, form: PublicationForm) -> HttpResponse:
        if refresh_from_pubmed(form.instance):
            form.instance.added_by = self.request.user
            return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data. Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("publication-create")


class PublicationDetail(ProtectedViewMixin, DetailView):
    model = Publication
    template_name = "publication/detail.html"


@protected_view
def publication_refresh(request: HttpRequest, slug: str) -> HttpResponse:
    """Updates a publication with the latest data from PubMed.

    Returns:
        Redirect to the publication detail page, with a warning if PubMed failed.
    """
    if request.method != "POST":
        return redirect("publication-detail", slug=slug)

    publication = get_object_or_404(Publication, slug=slug)
    if refresh_from_pubmed(publication):
        publication.save()
    else:
        messages.warning(request, REFRESH_FAILED_MESSAGE)
    return redirect("publication-detail", slug=slug)


class PublicationHistory(ProtectedViewMixin, DetailView):
    model = Publication
    template_name = "publication/history.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Publication, self.object)
        history_table = HistoryTable(
            obj.history.all(),  # type: ignore
            change_url_name="publication-change",
            change_url_slug1=obj.slug,
        )
        RequestConfig(self.request).configure(history_table)
        context["history_table"] = history_table
        return context


class PublicationChange(ProtectedViewMixin, DetailView):
    model = Publication
    template_name = "publication/change.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Publication, self.object)
        record = obj.history.get(history_id=self.kwargs["history_id"])  # type: ignore
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Publication, record, prev_record)
        return context


class PublicationList(ProtectedViewMixin, SearchListView):  # ty: ignore[invalid-method-override]
    model = Publication
    template_name = "publication/list.html"
    ordering = ["-updated_at"]
    table_class = PublicationTable
    search_fields = ["slug", "title", "author", "authors", "pubmed_id"]
    table_pagination = {"per_page": 25}
