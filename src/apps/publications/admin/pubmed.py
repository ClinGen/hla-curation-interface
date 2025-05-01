"""Configure the admin page for the pubmed model."""

from django.contrib import admin

from apps.publications.models.pubmed import PubMedArticle

admin.site.register(PubMedArticle)
