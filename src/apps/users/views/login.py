"""Provide a login view."""

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.users.forms.login import LoginForm


def custom_login(request: HttpRequest) -> HttpResponse:
    """Return the login form."""
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect(request.GET.get("next", "home"))
    else:
        form = LoginForm()
    return render(request, "users/login.html", {"form": form})
