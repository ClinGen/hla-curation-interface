"""Configures URLs for the core app."""

from django.urls import path

from firebase import views

urlpatterns = [
    path("sign-in", views.sign_in, name="sign-in"),
]
