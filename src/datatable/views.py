"""Provides a generic datatable view."""

from django.contrib.admin.views.decorators import staff_member_required
from django.core.paginator import Paginator
from django.db.models import Model
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from datatable.constants import FieldTypes
from datatable.metadata import FIELDS
from datatable.models import Pokemon
from datatable.queries import filter_, search, sort

DEFAULT_ITEMS_PER_PAGE = 50


def datatable(
    request: HttpRequest,
    model: type[Model],
    order_by: str,
    fields: list[dict],
    data_title: str,
    template: str = "datatable/view.html",
    partial: str = "datatable/partials/content.html",
) -> HttpResponse:
    """Returns a datatable for the given model.

    Args:
        request: The Django HttpRequest object.
        model: The model we want a datatable for.
        order_by: The parameter to order the objects by.
        fields: The metadata about the model fields.
        data_title: The title of the data used in the main heading and elsewhere.
        template: The full template for the view.
        partial: The partial template for HTMX responses.
    """
    queryset = model.objects.all().order_by(order_by)  # type: ignore

    for field in fields:
        if field["type"] == FieldTypes.SEARCH:
            queryset = search(request, queryset, field["param_name"])
        elif field["type"] == FieldTypes.SORT:
            queryset = sort(request, queryset, field["param_name"])
        elif field["type"] == FieldTypes.FILTER:
            queryset = filter_(request, queryset, field["param_name"])

    req_page = request.GET.get("page")
    page_num = req_page if req_page else 1
    paginator = Paginator(queryset, DEFAULT_ITEMS_PER_PAGE)
    page = paginator.page(page_num)

    context = {
        "page": page,
        "paginator": paginator,
        "fields": fields,
        "data_title": data_title,
        "partial": partial,
    }

    if request.headers.get("Hx-Request"):
        return render(request, partial, context)
    return render(request, template, context)


@staff_member_required
def pokemon(request: HttpRequest) -> HttpResponse:
    """Returns a datatable for Pokémon.

    This view is only used for tests.
    """
    return datatable(
        request=request,
        model=Pokemon,
        order_by="pokedex_number",
        fields=FIELDS,  # type: ignore
        data_title="Pokémon",
    )
