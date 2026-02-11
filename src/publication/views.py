from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView

from auth_.permissions import CreateAccessMixin
from publication.clients import (
    fetch_pubmed_data,
    fetch_rxiv_data,
    get_pubmed_author,
    get_pubmed_title,
    get_pubmed_year,
    get_rxiv_author,
    get_rxiv_title,
    get_rxiv_year,
)
from publication.constants.models import PublicationTypes
from publication.forms import PublicationForm
from publication.models import Publication


class PublicationCreate(CreateAccessMixin, CreateView):  # type: ignore
    model = Publication
    form_class = PublicationForm
    template_name = "publication/create.html"
    success_url = reverse_lazy("publication-list")

    def form_valid(self, form: PublicationForm) -> HttpResponse:
        if form.instance.publication_type == PublicationTypes.PUBMED:
            pubmed_data = fetch_pubmed_data(form.instance.pubmed_id)
            if pubmed_data:
                form.instance.author = get_pubmed_author(pubmed_data)
                form.instance.title = get_pubmed_title(pubmed_data)
                form.instance.publication_year = get_pubmed_year(pubmed_data)
                form.instance.added_by = self.request.user
                messages.success(self.request, "Publication created.")
                return super().form_valid(form)
        elif (
            form.instance.publication_type == PublicationTypes.BIORXIV
            or form.instance.publication_type == PublicationTypes.MEDRXIV
        ):
            rxiv_data = fetch_rxiv_data(
                form.instance.publication_type, form.instance.doi
            )
            if rxiv_data:
                form.instance.author = get_rxiv_author(rxiv_data)
                form.instance.title = get_rxiv_title(rxiv_data)
                form.instance.publication_year = get_rxiv_year(rxiv_data)
                form.instance.added_by = self.request.user
                return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data from PubMed. "
            "Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("disease-create")


class PublicationDetail(DetailView):
    model = Publication
    template_name = "publication/detail.html"


class PublicationList(ListView):
    model = Publication
    template_name = "publication/list.html"
