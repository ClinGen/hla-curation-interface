"""Configures URLs for the core app."""

from django.urls import path

from firebase import views

urlpatterns = [
    path("verify", views.verify, name="verify"),
    path("signup", views.signup, name="signup"),
    path("login", views.login_, name="login"),
    path("logout", views.logout_, name="logout"),
    path("profile/view", views.profile_view, name="profile_view"),
    path("profile/edit", views.profile_edit, name="profile_edit"),
]
