"""Define the URLs for the users app."""

from django.urls import path

from apps.users.views.logout import custom_logout
from apps.users.views.signup import custom_signup

urlpatterns = [
    path("signup", custom_signup, name="signup"),
    path("logout", custom_logout, name="logout"),
]
