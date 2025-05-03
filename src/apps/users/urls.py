"""Define the URLs for the users app."""

from django.urls import path

from apps.users.views.login import custom_login
from apps.users.views.logout import custom_logout
from apps.users.views.profile import profile
from apps.users.views.signup import custom_signup

urlpatterns = [
    path("login", custom_login, name="login"),
    path("logout", custom_logout, name="logout"),
    path("<str:username>/profile", profile, name="profile"),
    path("signup", custom_signup, name="signup"),
]
