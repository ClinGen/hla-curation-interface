from django.contrib import messages
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from auth_.permissions import CreateAccessMixin
from haplotype.constants.models import GENE_LIST
from haplotype.forms import HaplotypeForm
from haplotype.models import Haplotype


class HaplotypeCreate(CreateAccessMixin, CreateView):  # type: ignore
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
        name = [item["allele"] for item in sorted_alleles]
        form.instance.name = "~".join(name)
        form.instance.added_by = self.request.user
        messages.success(self.request, "Added haplotype.")
        return super().form_valid(form)


class HaplotypeDetail(DetailView):
    model = Haplotype
    template_name = "haplotype/detail.html"


class HaplotypeList(ListView):
    model = Haplotype
    template_name = "haplotype/list.html"
