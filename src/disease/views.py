from typing import cast

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django_tables2 import RequestConfig

from auth_.permissions import ProtectedViewMixin
from common.history import resolve_changes
from common.tables import HistoryTable
from common.views import SearchListView
from curation.tables import CurationTable
from disease.clients import fetch_disease_data, get_iri, get_name
from disease.forms import DiseaseForm
from disease.models import Disease
from disease.tables import DiseaseTable


class DiseaseCreate(ProtectedViewMixin, CreateView):
    model = Disease
    form_class = DiseaseForm
    template_name = "disease/create.html"
    success_url = reverse_lazy("disease-list")

    def form_valid(self, form: DiseaseForm) -> HttpResponse:
        disease_data = fetch_disease_data(form.instance.mondo_id)
        if disease_data:
            form.instance.name = get_name(disease_data)
            form.instance.iri = get_iri(disease_data)
            form.instance.added_by = self.request.user
            messages.success(self.request, "Disease added.")
            return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data from the "
            "Ontology Lookup Service. Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("disease-create")


class DiseaseDetail(ProtectedViewMixin, DetailView):
    model = Disease
    template_name = "disease/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Disease, self.object)
        curation_table = CurationTable(obj.curations.all())  # type: ignore
        RequestConfig(self.request).configure(curation_table)
        context["curation_table"] = curation_table
        return context


class DiseaseHistory(ProtectedViewMixin, DetailView):
    model = Disease
    template_name = "disease/history.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Disease, self.object)
        history_table = HistoryTable(
            obj.history.all(),  # type: ignore
            change_url_name="disease-change",
            change_url_slug1=obj.slug,
        )
        RequestConfig(self.request).configure(history_table)
        context["history_table"] = history_table
        return context


class DiseaseChange(ProtectedViewMixin, DetailView):
    model = Disease
    template_name = "disease/change.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Disease, self.object)
        record = obj.history.get(history_id=self.kwargs["history_id"])  # type: ignore
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Disease, record, prev_record)
        return context


class DiseaseList(ProtectedViewMixin, SearchListView):
    model = Disease
    template_name = "disease/list.html"
    ordering = ["-updated_at"]
    table_class = DiseaseTable
    search_fields = ["slug", "name", "mondo_id"]
    table_pagination = {"per_page": 25}
