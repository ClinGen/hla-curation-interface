from django.db.models import Q, QuerySet
from django.views.generic import ListView
from django_tables2 import SingleTableMixin


class SearchListView(SingleTableMixin, ListView):
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
        return self.object_list

    def get_template_names(self) -> list[str]:
        if self.request.headers.get("HX-Request"):
            return ["common/partials/search_results.html"]
        return super().get_template_names()

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["result_count"] = self.object_list.count()
        return context
