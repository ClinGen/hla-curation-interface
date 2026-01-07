"""Configures URLs for the auth_ app."""

from django.urls import path

from auth_ import views

urlpatterns = [
    path("login", views.login_, name="login"),
    path("callback", views.callback, name="callback"),
    path("logout", views.logout_, name="logout"),
    path("profile", views.profile, name="profile"),
    path("phi", views.phi, name="phi"),
]
