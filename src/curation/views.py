"""Provides views for the curation app."""

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin, has_create_access
from curation.constants.views import CURATION_SEARCH_FIELDS, FRAMEWORK
from curation.forms import (
    CurationCreateForm,
    CurationEditForm,
    EvidenceCreateForm,
    EvidenceEditForm,
    EvidenceTopLevelEditFormSet,
)
from curation.models import (
    Curation,
    Evidence,
)
from curation.validators.views import (
    validate_beta,
    validate_ci_end,
    validate_ci_start,
    validate_effect_size_statistic,
    validate_odds_ratio,
    validate_p_value,
    validate_relative_risk,
)
from datatable.views import datatable


class CurationCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a curation."""

    model = Curation
    form_class = CurationCreateForm
    template_name = "curation/create.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"

    def form_valid(self, form: CurationCreateForm) -> HttpResponse:
        """Makes sure the user who added the curation is recorded.

        Returns:
             The details page for the curation if the form is valid, or the form with
             errors if the form isn't valid.
        """
        form.instance.added_by = self.request.user
        return super().form_valid(form)


class CurationDetail(DetailView):
    """Shows the user information about a curation."""

    model = Curation
    template_name = "curation/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"


class CurationEdit(UpdateView):
    """Shows the user information about a curation."""

    model = Curation
    form_class = CurationEditForm
    template_name = "curation/edit_curation.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"


@has_create_access
def curation_edit_evidence(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Returns the editable curation details page with editable top-level evidence.

    Args:
         request: The Django request object.
         curation_slug: The curation object's slug (human-readable ID).
    """
    curation = get_object_or_404(Curation, slug=curation_slug)
    evidence = Evidence.objects.filter(curation=curation)
    if request.method == "POST":
        evidence_formset = EvidenceTopLevelEditFormSet(request.POST, queryset=evidence)
        if evidence_formset.is_valid():
            evidence_formset.save()
            messages.success(request, "Changes saved successfully.")
            return redirect("curation-detail", curation_slug=curation.slug)
    else:
        evidence_formset = EvidenceTopLevelEditFormSet(queryset=evidence)

    context = {
        "curation": curation,
        "evidence_formset": evidence_formset,
    }
    return render(request, "curation/edit_evidence.html", context)


def curation_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching curations."""
    return datatable(
        request=request,
        model=Curation,
        order_by="pk",
        fields=CURATION_SEARCH_FIELDS,  # type: ignore
        data_title="Curations",
        partial="curation/partials/search.html",
    )


class EvidenceCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) evidence."""

    model = Evidence
    form_class = EvidenceCreateForm
    template_name = "evidence/create.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def form_valid(self, form: EvidenceCreateForm) -> HttpResponse:
        """Makes sure the user who added the evidence is recorded.

        Returns:
             The details page for the evidence if the form is valid, or the form with
             errors otherwise.
        """
        curation = Curation.objects.get(slug=self.kwargs["curation_slug"])
        form.instance.curation = curation
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):  # noqa
        """Returns the context with the human-readable curation ID."""
        context = super().get_context_data(**kwargs)
        context["curation_slug"] = self.kwargs["curation_slug"]
        return context


class EvidenceDetail(DetailView):
    """Shows the user information about evidence."""

    model = Evidence
    template_name = "evidence/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def get_context_data(self, **kwargs):  # noqa
        """Returns the context with the framework."""
        context = super().get_context_data(**kwargs)
        context["framework"] = FRAMEWORK
        return context


class EvidenceEdit(UpdateView, CreateAccessMixin):  # type: ignore
    """Allows the user to edit evidence."""

    model = Evidence
    form_class = EvidenceEditForm
    template_name = "evidence/edit.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def form_invalid(self, form: EvidenceEditForm) -> HttpResponse:
        """Returns the form with errors and flashes a message about the errors."""
        message = (
            "There was an issue with your submission. Please check the form fields."
        )
        messages.error(self.request, message)
        return super().form_invalid(form)

    def form_valid(self, form: EvidenceEditForm) -> HttpResponse:
        """Sets the value for several fields that don't appear in the form.

        Also makes sure there is only one effect size statistic.

        Returns:
             The details page for the evidence.
        """
        validate_effect_size_statistic(form)
        validate_p_value(form)
        validate_odds_ratio(form)
        validate_relative_risk(form)
        validate_beta(form)
        validate_ci_start(form)
        validate_ci_end(form)
        return super().form_valid(form)
