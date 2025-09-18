"""Configures URLs for the repo app."""

from django.urls import path

from repo import views

urlpatterns = [
    path("", views.repo_home, name="repo-home"),
]
