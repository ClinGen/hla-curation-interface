from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from auth_.permissions import CreateAccessMixin
from disease.clients import fetch_disease_data, get_iri, get_name
from disease.forms import DiseaseForm
from disease.models import Disease


class DiseaseCreate(CreateAccessMixin, CreateView):  # type: ignore
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


class DiseaseDetail(DetailView):
    model = Disease
    template_name = "disease/detail.html"


class DiseaseList(ListView):
    model = Disease
    template_name = "disease/list.html"
