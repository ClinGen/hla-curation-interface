from typing import cast

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django_tables2 import RequestConfig

from auth_.permissions import ProtectedViewMixin
from common.history import resolve_changes
from common.tables import HistoryTable
from common.views import SearchListView
from publication.clients import (
    fetch_pubmed_data,
    get_pubmed_author,
    get_pubmed_title,
    get_pubmed_year,
)
from publication.forms import PublicationForm
from publication.models import Publication
from publication.tables import PublicationTable


class PublicationCreate(ProtectedViewMixin, CreateView):
    model = Publication
    form_class = PublicationForm
    template_name = "publication/create.html"
    success_url = reverse_lazy("publication-list")

    def form_valid(self, form: PublicationForm) -> HttpResponse:
        pubmed_data = fetch_pubmed_data(form.instance.pubmed_id)
        if pubmed_data:
            form.instance.author = get_pubmed_author(pubmed_data)
            form.instance.title = get_pubmed_title(pubmed_data)
            form.instance.publication_year = get_pubmed_year(pubmed_data)
            form.instance.added_by = self.request.user
            messages.success(self.request, "Publication created.")
            return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data. Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("publication-create")


class PublicationDetail(ProtectedViewMixin, DetailView):
    model = Publication
    template_name = "publication/detail.html"


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
    search_fields = ["slug", "title", "author", "pubmed_id"]
    table_pagination = {"per_page": 25}
