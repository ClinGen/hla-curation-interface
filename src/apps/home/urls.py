"""Define the URLs for the home app."""

from django.urls import path

from apps.home.views.home import home

urlpatterns = [
    path("", home, name="home"),
]
