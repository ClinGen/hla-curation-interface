"""Configures URLs for the project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
    path("allele/", include("allele.urls")),
    path("curation/", include("curation.urls")),
    path("datatable/", include("datatable.urls")),
    path("disease/", include("disease.urls")),
    path("firebase/", include("firebase.urls")),
    path("haplotype/", include("haplotype.urls")),
    path("publication/", include("publication.urls")),
    path("repo/", include("repo.urls")),
]
