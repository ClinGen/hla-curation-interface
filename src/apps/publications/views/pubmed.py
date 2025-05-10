"""Provide views for PubMed publications."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.publications.clients.pubmed import PubMedArticleClient
from apps.publications.components.params.tabs import (
    new_pubmed_publication_tabs,
    search_pubmed_publication_tabs,
)
from apps.publications.forms.pubmed import PubMedArticleForm
from apps.publications.selectors.pubmed import PubMedArticleSelector
from apps.publications.services.pubmed import PubMedArticleService
from base.views import EntityView
from constants import PubMedConstants


class PubMedView(EntityView):
    """Create, view all, or view a PubMed publication."""

    @staticmethod
    @login_required
    def new(request: HttpRequest) -> HttpResponse:
        """Return the view that provides a form that creates a PubMed publication."""
        if request.method == "POST":
            form = PubMedArticleForm(request.POST)
            if form.is_valid():
                pubmed_id = form.cleaned_data["pubmed_id"]
                client = PubMedArticleClient(pubmed_id)
                service = PubMedArticleService(client)
                service.create(pubmed_id)
                messages.success(request, "PubMed article created.")
                form = PubMedArticleForm()
        else:
            form = PubMedArticleForm()
        return render(
            request,
            "publications/pubmed/new.html",
            {
                "form": form,
                "tabs": new_pubmed_publication_tabs,
                "pubmed_search_url": PubMedConstants.SEARCH_URL,
            },
        )

    @staticmethod
    def list(request: HttpRequest) -> HttpResponse:
        """Return the searchable table page for a PubMed publication."""
        query = request.GET.get("q", None)
        selector = PubMedArticleSelector()
        articles = selector.list(query)

        if request.htmx:  # type: ignore (This attribute is added by the django-htmx app.)
            template_name = "publications/includes/pubmed_table.html"
        else:
            template_name = "publications/pubmed/list.html"

        return render(
            request,
            template_name,
            {"articles": articles, "tabs": search_pubmed_publication_tabs},
        )

    @staticmethod
    def details(request: HttpRequest, pubmed_id: str) -> HttpResponse:
        """Return the details page for a PubMed publication."""
        selector = PubMedArticleSelector()
        article = selector.get(pubmed_id=pubmed_id)
        context = {"article": article}
        return render(request, "publications/pubmed/details.html", context)
