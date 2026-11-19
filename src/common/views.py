import logging
import re
from typing import cast

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.db.models import Model, Q, QuerySet
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from django.views.generic import ListView
from django_tables2 import SingleTableMixin

logger = logging.getLogger(__name__)


class SearchListView(SingleTableMixin, ListView):  # ty: ignore[invalid-method-override]
    search_fields: list[str] = []

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        q = self.request.GET.get("q", "").strip()
        if q and self.search_fields:
            filters = Q()
            for field in self.search_fields:
                filters |= Q(**{f"{field}__icontains": q})
            qs = qs.filter(filters)
        return qs

    def get_table_data(self) -> QuerySet:
        return self.object_list  # ty: ignore[invalid-return-type]

    def get_template_names(self) -> list[str]:
        if self.request.headers.get("HX-Request"):
            return ["common/partials/search_results.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["result_count"] = self.object_list.count()
        return context


class SuggestView(View):
    """Suggests existing records as a curator types, for an input with suggest_url.

    Subclasses set the model and the fields to search. The response is the
    common/partials/suggestions.html fragment, which suggest.js shows under the input.
    """

    model: type[Model]
    search_fields: list[str] = []
    ordering: list[str] = []
    min_length = 2
    limit = 10
    template_name = "common/partials/suggestions.html"

    def get_suggestion(self, obj: Model) -> tuple[str, str]:
        """Returns what to fill the input with and what to show for a record.

        Args:
            obj: A matching record.

        Returns:
            The value for the input and the text to show, both the record's string by
            default.
        """
        return str(obj), str(obj)

    def get_matches(self, q: str) -> QuerySet:
        """Returns the records with q in any of the search fields.

        Args:
            q: The typed text, at least min_length characters long.

        Returns:
            The matching records, ordered.
        """
        filters = Q()
        for field in self.search_fields:
            filters |= Q(**{f"{field}__icontains": q})
        return self.model.objects.filter(filters).order_by(*self.ordering)

    def get(self, request: HttpRequest) -> HttpResponse:
        """Renders up to limit records that match the query in q.

        Returns:
            The suggestions fragment, empty if q is shorter than min_length.
        """
        q = request.GET.get("q", "").strip()
        suggestions = []
        if len(q) >= self.min_length:
            matches = self.get_matches(q)
            suggestions = [self.get_suggestion(obj) for obj in matches[: self.limit]]
        return render(request, self.template_name, {"suggestions": suggestions})


class BackupDatabaseView(View):
    """Backs up the database under manual/, for the admin's Back up now button.

    The backup runs inside the request. The database is small, so it takes well under
    Gunicorn's timeout. Only POST is allowed, so a GET gets a 405.
    """

    def post(self, request: HttpRequest) -> HttpResponse:
        """Back up the database if the user is a superuser.

        Args:
            request: The request from a staff user.

        Returns:
            A redirect to the admin index, with a message saying how the backup went.

        Raises:
            PermissionDenied: If the user isn't a superuser.
        """
        user = cast("User", request.user)
        if not user.is_superuser:
            raise PermissionDenied
        # Usernames are email addresses. Keep backup names to safe characters.
        username = re.sub(r"[^A-Za-z0-9.-]+", "-", user.get_username())
        timestamp = timezone.now().strftime("%Y-%m-%dT%H%M%SZ")
        name = f"manual/{settings.DBBACKUP_HOSTNAME}-{username}-{timestamp}.sqlite3.gz"
        try:
            call_command("dbbackup", "--noinput", "--compress", "-o", name)
        except Exception:
            logger.exception(f"Manual database backup to {name} failed")
            messages.error(request, "The backup failed. The error has been logged.")
        else:
            messages.success(request, f"Backed up the database to {name}.")
        return redirect("admin:index")
