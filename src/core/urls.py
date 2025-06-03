"""Configures URLs for the core app."""

from django.urls import path

from core import views

urlpatterns = [
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("acknowledgements", views.acknowledgements, name="acknowledgements"),
    path("citing", views.citing, name="citing"),
    path("collaborators", views.collaborators, name="collaborators"),
    path("contact", views.contact, name="contact"),
    path("downloads", views.downloads, name="downloads"),
    path("help", views.help_, name="help"),
    path("login", views.login, name="login"),
]
