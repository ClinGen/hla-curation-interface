from typing import cast

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from auth_.permissions import ProtectedViewMixin
from common.history import resolve_changes
from disease.clients import fetch_disease_data, get_iri, get_name
from disease.forms import DiseaseForm
from disease.models import Disease


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


class DiseaseHistory(ProtectedViewMixin, DetailView):
    model = Disease
    template_name = "disease/history.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Disease, self.object)
        context["history"] = obj.history.all()  # type: ignore
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


class DiseaseList(ProtectedViewMixin, ListView):
    model = Disease
    template_name = "disease/list.html"
    ordering = ["-updated_at"]
