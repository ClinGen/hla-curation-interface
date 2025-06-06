"""Configures URLs for the core app."""

from django.urls import path

from firebase import views

urlpatterns = [
    path("login", views.login_, name="login"),
    path("verify", views.verify, name="verify"),
]
