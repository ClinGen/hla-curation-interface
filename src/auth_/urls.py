from django.urls import path

from auth_ import views

urlpatterns = [
    path("login", views.login_, name="login"),
    path("callback", views.callback, name="callback"),
    path("logout", views.logout_, name="logout"),
    path("clerk/login", views.clerk_login, name="clerk_login"),
    path("clerk/callback", views.clerk_callback, name="clerk_callback"),
    path("clerk/logout", views.clerk_logout, name="clerk_logout"),
    path("profile", views.profile, name="profile"),
    path("phi", views.phi, name="phi"),
]
