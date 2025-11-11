"""Defines permissions for the core app and other apps."""

from collections.abc import Callable
from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect

from config.settings.base import LOGIN_URL

PERMISSION_DENIED_MESSAGE = "You don't have permission to access this page."


class CreateAccessMixin(AccessMixin):
    """Ensures the user has the correct permissions creating.

    This AccessMixin should be used in class-based views that aren't public.
    """

    def dispatch(
        self,
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse | HttpResponseRedirect | None:
        """Defines permission logic.

        Raises:
            PermissionDenied: When the user doesn't have correct permissions.

        Returns:
            If the user has the correct permissions, the requested view is returned.
            Otherwise, the user is redirected to the login view.
        """
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if hasattr(request.user, "profile") and request.user.profile.can_create:
            return super().dispatch(request, *args, **kwargs)  # type: ignore
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)


def has_create_access(view_function: Callable) -> Callable:
    """Ensures the user has the correct permissions for creating.

    This decorator should be used in function-based views that aren't public.

    Returns:
        The view function wrapped with permissions logic.
    """

    @wraps(view_function)
    def _wrapped_view(
        request: HttpRequest,
        *args,
        **kwargs,
    ) -> HttpResponse | HttpResponseRedirect | None:
        """Defines permission logic.

        Raises:
            PermissionDenied: When the user doesn't have correct permissions.

        Returns:
            If the user has the correct permissions, the requested view is returned.
            Otherwise, the user is redirected to the login view.
        """
        if not request.user.is_authenticated:
            return redirect(f"{LOGIN_URL}?next={request.path}")
        if hasattr(request.user, "profile") and request.user.profile.can_create:
            return view_function(request, *args, **kwargs)
        raise PermissionDenied(PERMISSION_DENIED_MESSAGE)

    return _wrapped_view
