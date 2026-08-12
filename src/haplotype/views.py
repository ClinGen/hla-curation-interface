from typing import cast

from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django_tables2 import RequestConfig

from allele.tables import AlleleTable
from auth_.permissions import ProtectedViewMixin
from common.history import resolve_changes
from common.tables import HistoryTable
from common.views import SearchListView
from curation.tables import CurationTable
from haplotype.constants.models import GENE_LIST
from haplotype.forms import HaplotypeForm
from haplotype.models import Haplotype
from haplotype.tables import HaplotypeTable


class HaplotypeCreate(ProtectedViewMixin, CreateView):
    model = Haplotype
    form_class = HaplotypeForm
    template_name = "haplotype/create.html"
    success_url = reverse_lazy("haplotype-list")

    def form_valid(self, form: HaplotypeForm) -> HttpResponse:
        """Sets the haplotype name by sorting the constituent alleles.

        Returns:
             The success page if valid or the form with errors if not.
        """
        unsorted_alleles: list[tuple[str, int]] = []
        for allele in form.cleaned_data["alleles"]:
            gene = allele.name.split("*")[0]
            index = GENE_LIST.index(gene)
            unsorted_alleles.append((allele.name, index))
        sorted_alleles = sorted(unsorted_alleles, key=lambda item: item[1])
        computed_name = "~".join(item[0] for item in sorted_alleles)
        if Haplotype.objects.filter(name=computed_name).exists():
            form.add_error("alleles", "A haplotype with these alleles already exists.")
            return self.form_invalid(form)
        form.instance.name = computed_name
        form.instance.added_by = self.request.user
        messages.success(self.request, "Added haplotype.")
        return super().form_valid(form)


class HaplotypeDetail(ProtectedViewMixin, DetailView):
    model = Haplotype
    template_name = "haplotype/detail.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Haplotype, self.object)
        allele_table = AlleleTable(obj.alleles.all(), prefix="allele_")
        curation_table = CurationTable(obj.curations.all(), prefix="curation_")  # type: ignore
        RequestConfig(self.request).configure(allele_table)
        RequestConfig(self.request).configure(curation_table)
        context["allele_table"] = allele_table
        context["curation_table"] = curation_table
        return context


class HaplotypeHistory(ProtectedViewMixin, DetailView):
    model = Haplotype
    template_name = "haplotype/history.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Haplotype, self.object)
        history_table = HistoryTable(
            obj.history.all(),  # type: ignore
            change_url_name="haplotype-change",
            change_url_slug1=obj.slug,
        )
        RequestConfig(self.request).configure(history_table)
        context["history_table"] = history_table
        return context


class HaplotypeChange(ProtectedViewMixin, DetailView):
    model = Haplotype
    template_name = "haplotype/change.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Haplotype, self.object)
        record = obj.history.get(history_id=self.kwargs["history_id"])  # type: ignore
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Haplotype, record, prev_record)
        return context


class HaplotypeList(ProtectedViewMixin, SearchListView):
    model = Haplotype
    template_name = "haplotype/list.html"
    ordering = ["-updated_at"]
    table_class = HaplotypeTable
    search_fields = ["slug", "name"]
    table_pagination = {"per_page": 25}
