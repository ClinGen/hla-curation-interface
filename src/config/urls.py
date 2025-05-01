"""Configure URLs for the project."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("apps.home.urls")),
    path("curations/", include("apps.curations.urls")),
    path("diseases/", include("apps.diseases.urls")),
    path("markers/", include("apps.markers.urls")),
    path("publications/", include("apps.publications.urls")),
    path("users/", include("apps.users.urls")),
    path("admin/", admin.site.urls),
]
