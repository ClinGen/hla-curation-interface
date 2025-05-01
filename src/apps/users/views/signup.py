"""Provide a signup view for first-time users."""

from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.users.forms.signup import SignupForm


def signup(request: HttpRequest) -> HttpResponse:
    """Return the signup form."""
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("home")
    else:
        form = SignupForm()
    return render(request, "users/signup.html", {"form": form})
