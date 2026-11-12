from typing import cast

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from django_tables2 import RequestConfig

from allele.forms import AlleleForm
from allele.models import Allele
from allele.tables import AlleleTable
from auth_.permissions import ProtectedViewMixin
from common.history import resolve_changes
from common.tables import HistoryTable
from common.views import SearchListView
from curation.tables import CurationTable
from haplotype.tables import HaplotypeTable


class AlleleCreate(ProtectedViewMixin, CreateView):
    model = Allele
    form_class = AlleleForm
    template_name = "allele/create.html"
    success_url = reverse_lazy("allele-list")

    def form_valid(self, form: AlleleForm) -> HttpResponse:
        """Fetches and adds data from the ClinGen Allele Registry and records user.

        Returns:
             The success page for the allele if the form is valid, or the form with
             errors if the form isn't valid.
        """
        try:
            allele = Allele.get_or_build(form.instance.name)
        except ValidationError as error:
            messages.warning(self.request, error.messages[0])
            return redirect("allele-create")
        form.instance.car_id = allele.car_id
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class AlleleDetail(ProtectedViewMixin, DetailView):
    model = Allele
    template_name = "allele/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Allele, self.object)
        haplotype_table = HaplotypeTable(obj.haplotypes.all(), prefix="haplotype_")  # type: ignore
        curation_table = CurationTable(obj.curations.all(), prefix="curation_")  # type: ignore
        RequestConfig(self.request).configure(haplotype_table)
        RequestConfig(self.request).configure(curation_table)
        context["haplotype_table"] = haplotype_table
        context["curation_table"] = curation_table
        return context


class AlleleHistory(ProtectedViewMixin, DetailView):
    model = Allele
    template_name = "allele/history.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Allele, self.object)
        history_table = HistoryTable(
            obj.history.all(),  # type: ignore
            change_url_name="allele-change",
            change_url_slug1=obj.slug,
        )
        RequestConfig(self.request).configure(history_table)
        context["history_table"] = history_table
        return context


class AlleleChange(ProtectedViewMixin, DetailView):
    model = Allele
    template_name = "allele/change.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Allele, self.object)
        record = obj.history.get(history_id=self.kwargs["history_id"])  # type: ignore
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Allele, record, prev_record)
        return context


class AlleleList(ProtectedViewMixin, SearchListView):  # ty: ignore[invalid-method-override]
    model = Allele
    template_name = "allele/list.html"
    ordering = ["-updated_at"]
    table_class = AlleleTable
    search_fields = ["slug", "name", "car_id"]
    table_pagination = {"per_page": 25}
