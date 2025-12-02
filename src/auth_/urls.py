"""Configures URLs for the auth_ app."""

from django.urls import path

from auth_ import views

urlpatterns = [
    path("login", views.login, name="woslogin"),
    path("callback", views.callback, name="woscallback"),
]
