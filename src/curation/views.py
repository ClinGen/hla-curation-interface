from typing import cast

from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.http import (
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView
from django.views.generic.edit import CreateView, UpdateView

from auth_.permissions import (
    ProtectedViewMixin,
    protected_view,
    reviewer_view,
)
from common.history import resolve_changes
from curation.constants.models.common import Status
from curation.constants.views import FRAMEWORK
from curation.forms import (
    CurationCreateForm,
    EPReviewForm,
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
    validate_has_association_and_p_value,
    validate_odds_ratio,
    validate_relative_risk,
)


class CurationCreate(ProtectedViewMixin, CreateView):
    model = Curation
    form_class = CurationCreateForm
    template_name = "curation/create.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"
    success_url = reverse_lazy("curation-list")

    def form_valid(self, form: CurationCreateForm) -> HttpResponse:
        form.instance.added_by = self.request.user
        messages.success(self.request, "Curation added.")
        return super().form_valid(form)


class CurationDetail(ProtectedViewMixin, DetailView):
    model = Curation
    template_name = "curation/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"


@protected_view
def curation_edit_evidence(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Returns the editable curation details page with editable top-level evidence.

    Args:
         request: The Django request object.
         curation_slug: The curation object's slug (human-readable ID).
    """
    curation = get_object_or_404(Curation, slug=curation_slug)

    if curation.is_locked:
        messages.error(request, "This curation is locked and cannot be edited.")
        return redirect("curation-detail", curation_slug=curation.slug)

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
        "object": curation,
        "evidence_formset": evidence_formset,
    }
    return render(request, "curation/edit/evidence.html", context)


class EvidenceCreate(ProtectedViewMixin, CreateView):
    model = Evidence
    form_class = EvidenceCreateForm
    template_name = "evidence/create.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def dispatch(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponse | HttpResponseRedirect | None:
        curation = get_object_or_404(Curation, slug=kwargs.get("curation_slug"))
        if curation.is_locked:
            messages.error(request, "This curation is locked and cannot be edited.")
            return redirect("curation-detail", curation_slug=curation.slug)
        return super().dispatch(request, *args, **kwargs)  # type: ignore[return-value]

    def form_valid(self, form: EvidenceCreateForm) -> HttpResponse:
        curation = Curation.objects.get(slug=self.kwargs["curation_slug"])
        form.instance.curation = curation
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):  # noqa
        """Returns the context with the human-readable curation ID."""
        context = super().get_context_data(**kwargs)
        context["curation_slug"] = self.kwargs["curation_slug"]
        return context


class EvidenceDetail(ProtectedViewMixin, DetailView):
    model = Evidence
    template_name = "evidence/detail.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def get_context_data(self, **kwargs):  # noqa
        """Returns the context with the framework."""
        context = super().get_context_data(**kwargs)
        context["framework"] = FRAMEWORK
        return context


class EvidenceEdit(ProtectedViewMixin, UpdateView):
    model = Evidence
    form_class = EvidenceEditForm
    template_name = "evidence/edit.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def dispatch(
        self, request: HttpRequest, *args, **kwargs
    ) -> HttpResponse | HttpResponseRedirect | None:
        """Check if parent curation is locked before allowing edit.

        Returns:
            Redirect to evidence detail if locked, otherwise the normal dispatch result.
        """
        self.object = self.get_object()
        curation = self.object.curation
        if curation.is_locked:
            messages.error(
                request,
                "This evidence belongs to a locked curation and cannot be edited.",
            )
            return redirect(
                "evidence-detail",
                curation_slug=curation.slug,
                evidence_slug=self.object.slug,
            )
        return super().dispatch(request, *args, **kwargs)  # type: ignore[return-value]

    def form_invalid(self, form: EvidenceEditForm) -> HttpResponse:
        message = (
            "There was an issue with your submission. Please check the form fields."
        )
        messages.error(self.request, message)
        return super().form_invalid(form)

    def form_valid(self, form: EvidenceEditForm) -> HttpResponse:
        validate_effect_size_statistic(form)
        validate_has_association_and_p_value(form)
        validate_odds_ratio(form)
        validate_relative_risk(form)
        validate_beta(form)
        validate_ci_start(form)
        validate_ci_end(form)

        if form.errors:
            return self.form_invalid(form)

        return super().form_valid(form)


@protected_view
def curation_publish(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Publishes a provisional curation to the repository.

    Returns:
        Redirect to the repo detail page on success, or curation detail on error.
    """
    from repo.models import PublishedCuration

    curation = get_object_or_404(Curation, slug=curation_slug)
    try:
        with transaction.atomic():
            curation.transition_to(Status.PUBLISHED)
            PublishedCuration.objects.create(
                curation=curation,
                published_by=cast(User, request.user),
            )
    except ValueError as e:
        messages.error(request, str(e))
        return redirect("curation-detail", curation_slug=curation.slug)

    messages.success(
        request,
        f"Curation {curation.slug} has been published to the repository.",
    )
    return redirect("repo-detail", curation_slug=curation.slug)


@protected_view
def curation_submit(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Submits a curation for EP review.

    Returns:
        Redirect to curation detail, with success or error messages set.
    """
    if request.method != "POST":
        return redirect("curation-detail", curation_slug=curation_slug)

    curation = get_object_or_404(Curation, slug=curation_slug)
    errors = curation.can_submit()
    if errors:
        for err in errors:
            messages.error(request, err)
        return redirect("curation-detail", curation_slug=curation.slug)

    curation.transition_to(Status.READY_FOR_REVIEW)
    messages.success(
        request, f"Curation {curation.slug} has been submitted for review."
    )
    return redirect("curation-detail", curation_slug=curation.slug)


@reviewer_view
def curation_review(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Renders and processes the EP review form.

    Returns:
        Redirect on POST success, or the review form page on GET.
    """
    curation = get_object_or_404(Curation, slug=curation_slug)

    if request.method == "POST":
        form = EPReviewForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data["decision"]
            curation.ep_classification = form.cleaned_data["ep_classification"] or None
            curation.ep_evidence_summary = (
                form.cleaned_data["ep_evidence_summary"] or None
            )
            curation.ep_additional_notes = (
                form.cleaned_data["ep_additional_notes"] or None
            )
            curation.ep = form.cleaned_data["ep"] or None
            if decision == "needs_revision":
                curation.transition_to(Status.IN_PROGRESS)
                messages.info(
                    request,
                    f"Curation {curation.slug} has been sent back for revision.",
                )
            else:
                curation.transition_to(Status.PROVISIONAL)
                messages.success(
                    request, f"Curation {curation.slug} has been approved."
                )
            return redirect("curation-detail", curation_slug=curation.slug)
    else:
        form = EPReviewForm(
            initial={
                "ep_classification": curation.ep_classification,
                "ep_evidence_summary": curation.ep_evidence_summary,
                "ep_additional_notes": curation.ep_additional_notes,
                "ep": curation.ep,
            }
        )

    context = {"object": curation, "form": form}
    return render(request, "curation/review.html", context)


@protected_view
def curation_fork(request: HttpRequest, curation_slug: str) -> HttpResponse:
    """Creates a new editable curation forked from a published one.

    Returns:
        Redirect to the new fork's detail page, or curation detail on non-POST.
    """
    if request.method != "POST":
        return redirect("curation-detail", curation_slug=curation_slug)

    source = get_object_or_404(Curation, slug=curation_slug)

    if source.status != Status.PUBLISHED:
        from django.http import HttpResponseBadRequest

        return HttpResponseBadRequest("Only published curations can be forked.")

    with transaction.atomic():
        new_curation = Curation.objects.create(
            forked_from=source,
            curation_type=source.curation_type,
            allele=source.allele,
            haplotype=source.haplotype,
            disease=source.disease,
            status=Status.IN_PROGRESS,
            added_by=cast(User, request.user),
        )
        for evidence in source.evidence.prefetch_related("demographics").all():  # type: ignore
            evidence.copy_to(new_curation, added_by=cast(User, request.user))

    messages.success(request, f"Forked curation created as {new_curation.slug}.")
    return redirect("curation-detail", curation_slug=new_curation.slug)


class CurationHistory(ProtectedViewMixin, DetailView):
    model = Curation
    template_name = "curation/history.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Curation, self.object)
        context["history"] = obj.history.all()  # type: ignore
        return context


class CurationChange(ProtectedViewMixin, DetailView):
    model = Curation
    template_name = "curation/change.html"
    slug_field = "slug"
    slug_url_kwarg = "curation_slug"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Curation, self.object)
        record = obj.history.get(history_id=self.kwargs["history_id"])  # type: ignore
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Curation, record, prev_record)
        return context


class EvidenceHistory(ProtectedViewMixin, DetailView):
    model = Evidence
    template_name = "evidence/history.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Evidence, self.object)
        context["history"] = obj.history.all()  # type: ignore
        context["curation_slug"] = self.kwargs["curation_slug"]
        return context


class EvidenceChange(ProtectedViewMixin, DetailView):
    model = Evidence
    template_name = "evidence/change.html"
    slug_field = "slug"
    slug_url_kwarg = "evidence_slug"

    def get_context_data(self, **kwargs: object) -> dict:
        context = super().get_context_data(**kwargs)
        obj = cast(Evidence, self.object)
        record = obj.history.get(history_id=self.kwargs["history_id"])  # type: ignore
        prev_record = record.prev_record
        context["record"] = record
        context["changes"] = resolve_changes(Evidence, record, prev_record)
        context["curation_slug"] = self.kwargs["curation_slug"]
        return context


class CurationList(ProtectedViewMixin, ListView):
    model = Curation
    template_name = "curation/list.html"
    ordering = ["-updated_at"]
