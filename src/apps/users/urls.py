"""Define the URLs for the users app."""

from django.urls import path

from apps.users.views.signup import signup

urlpatterns = [
    path("signup", signup, name="signup"),
]
