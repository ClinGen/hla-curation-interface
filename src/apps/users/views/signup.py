"""Provide a signup view for first-time users."""

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.users.forms.signup import SignupForm
from apps.users.services.curator import new_curator


def custom_signup(request: HttpRequest) -> HttpResponse:
    """Return the signup form."""
    if request.user.is_authenticated:
        return redirect("home")
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            new_curator(user)
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})
