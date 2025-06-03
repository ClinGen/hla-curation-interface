"""Provides views for the firebase app."""

import json

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from firebase_admin import auth as firebase_auth


def login_(request: HttpRequest) -> HttpResponse:
    """Returns the login page."""
    return render(request, "firebase/login.html")


def extract_first_name(name: str) -> str:
    """Returns the first name from a full name string."""
    if not name or not name.strip():
        return ""
    name_parts = name.strip().split()
    return name_parts[0] if name_parts else ""


def extract_last_name(name: str) -> str:
    """Returns the last name from a full name string."""
    if not name or not name.strip():
        return ""
    name_parts = name.strip().split()
    return " ".join(name_parts[1:]) if len(name_parts) > 1 else ""


AUTH_SUCCESS = {
    "success": True,
    "message": "Authentication successful",
    "redirect_url": "/dashboard/",
}

AUTH_FAILURE = {
    "success": False,
    "message": "Authentication failed",
    "redirect_url": "/dashboard/",
}


@csrf_exempt
@require_http_methods(["POST"])
def auth(request: HttpRequest) -> JsonResponse:
    """Authenticates the user by verifying the Firebase ID token.

    Args:
        request: The Django HttpRequest object.

    Returns:
        The JSONResponse indicating whether the login was a success or a failure.
    """
    data = json.loads(request.body)
    id_token = data.get("id_token")
    decoded_token = firebase_auth.verify_id_token(id_token)
    uid = decoded_token["uid"]
    email = decoded_token.get("email", "")
    name = decoded_token.get("name", "")
    user, _ = User.objects.get_or_create(
        username=uid,
        email=email,
        first_name=extract_first_name(name),
        last_name=extract_last_name(name),
    )
    login(request, user)
    return JsonResponse(
        {
            "success": True,
            "message": "Authentication successful",
            "redirect_url": "/dashboard/",
        }
    )
