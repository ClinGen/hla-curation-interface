"""Define the URLs for the users app."""

from django.urls import path

from apps.users.views.login import custom_login
from apps.users.views.logout import custom_logout
from apps.users.views.signup import custom_signup

urlpatterns = [
    path("login", custom_login, name="login"),
    path("logout", custom_logout, name="logout"),
    path("signup", custom_signup, name="signup"),
]
