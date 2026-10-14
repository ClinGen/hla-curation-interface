"""Configures URLs for the project."""

from django.contrib import admin
from django.urls import include, path

from common.views import BackupDatabaseView

urlpatterns = [
    path("", include("core.urls")),
    path(
        "admin/backup/",
        admin.site.admin_view(BackupDatabaseView.as_view()),
        name="admin-backup",
    ),
    path("admin/", admin.site.urls),
    path("allele/", include("allele.urls")),
    path("auth/", include("auth_.urls")),
    path("curation/", include("curation.urls")),
    path("disease/", include("disease.urls")),
    path("haplotype/", include("haplotype.urls")),
    path("publication/", include("publication.urls")),
    path("repo/", include("repo.urls")),
]
