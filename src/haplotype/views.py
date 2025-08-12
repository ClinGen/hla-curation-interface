"""Provides views for the haplotype app."""

from django.http import HttpRequest, HttpResponse
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin
from datatable.constants.views import FieldTypes, SortDirections
from datatable.views import datatable
from haplotype.forms import HaplotypeForm
from haplotype.models import GENE_LIST, Haplotype


class HaplotypeCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a haplotype."""

    model = Haplotype
    form_class = HaplotypeForm
    template_name = "haplotype/create.html"

    def form_valid(self, form: HaplotypeForm) -> HttpResponse:
        """Sets the haplotype name and records user.

        Returns:
             The details page for the haplotype if the form is valid, or the form with
             errors if the form isn't valid.
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
        return super().form_valid(form)


class HaplotypeDetail(DetailView):
    """Shows the user information about a haplotype."""

    model = Haplotype
    template_name = "haplotype/detail.html"


# Define fields for use in the datatable.
FIELDS = [
    {
        "text": "ID",
        "param_name": "pk",
        "id": "pk",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Name",
        "param_name": "name",
        "id": "haplotype-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Added",
        "param_name": "added_at",
        "id": "added-at",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
]


def haplotype_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching haplotypes."""
    return datatable(
        request=request,
        model=Haplotype,
        order_by="pk",
        fields=FIELDS,  # type: ignore
        data_title="Haplotypes",
        partial="haplotype/partials/search.html",
    )
