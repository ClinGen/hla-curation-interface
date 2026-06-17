from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from auth_.permissions import ProtectedViewMixin
from common.history import resolve_changes
from haplotype.constants.models import GENE_LIST
from haplotype.forms import HaplotypeForm
from haplotype.models import Haplotype


class HaplotypeCreate(ProtectedViewMixin, CreateView):  # type: ignore
    model = Haplotype
    form_class = HaplotypeForm
    template_name = "haplotype/create.html"
    success_url = reverse_lazy("haplotype-list")

    def form_valid(self, form: HaplotypeForm) -> HttpResponse:
        """Sets the haplotype name by sorting the constituent alleles.

        Returns:
             The success page if valid or the form with errors if not.
        """
        unsorted_alleles = []
        for allele in form.cleaned_data["alleles"]:
            gene = allele.name.split("*")[0]
            index = GENE_LIST.index(gene)
            unsorted_alleles.append({"allele": allele.name, "index": index})
        sorted_alleles = sorted(unsorted_alleles, key=lambda item: item["index"])
        computed_name = "~".join(item["allele"] for item in sorted_alleles)
        if Haplotype.objects.filter(name=computed_name).exists():
            form.add_error("alleles", "A haplotype with these alleles already exists.")
            return self.form_invalid(form)
        form.instance.name = computed_name
        form.instance.added_by = self.request.user
        messages.success(self.request, "Added haplotype.")
        return super().form_valid(form)


class HaplotypeDetail(ProtectedViewMixin, DetailView):  # type: ignore
    model = Haplotype
    template_name = "haplotype/detail.html"


class HaplotypeHistory(ProtectedViewMixin, DetailView):  # type: ignore
    model = Haplotype
    template_name = "haplotype/history.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["history"] = self.object.history.all()  # type: ignore[union-attr]
        return context


class HaplotypeChange(ProtectedViewMixin, DetailView):  # type: ignore
    model = Haplotype
    template_name = "haplotype/change.html"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        record = self.object.history.get(history_id=self.kwargs["history_id"])  # type: ignore[union-attr]
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Haplotype, record, prev_record)
        return context


class HaplotypeList(ProtectedViewMixin, ListView):  # type: ignore
    model = Haplotype
    template_name = "haplotype/list.html"
    ordering = ["-updated_at"]
