from django.urls import path

from auth_ import views

urlpatterns = [
    path("login", views.login_, name="login"),
    path("callback", views.callback, name="callback"),
    path("logout", views.logout_, name="logout"),
    path("profile", views.profile, name="profile"),
    path("profile/history", views.profile_history, name="profile-history"),
    path(
        "profile/history/<int:history_id>/change",
        views.profile_change,
        name="profile-change",
    ),
    path("phi", views.phi, name="phi"),
]
