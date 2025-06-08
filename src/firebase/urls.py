"""Configures URLs for the core app."""

from django.urls import path

from firebase import views

urlpatterns = [
    path("verify", views.verify, name="verify"),
    path("signup", views.signup, name="signup"),
    path("login", views.login_, name="login"),
    path("logout", views.logout_, name="logout"),
]
