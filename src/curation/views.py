"""Provides views for the curation app."""

from decimal import Decimal

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView

from core.permissions import CreateAccessMixin, has_create_access
from curation.forms import (
    CurationCreateForm,
    CurationEditForm,
    EvidenceCreateForm,
    EvidenceEditForm,
    EvidenceTopLevelEditFormSet,
)
from curation.framework import Intervals, Points
from curation.models import (
    Curation,
    CurationTypes,
    EffectSizeStatistic,
    Evidence,
    Status,
)
from datatable.constants import FieldTypes, Filters, SortDirections
from datatable.views import datatable


class CurationCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) a curation."""

    model = Curation
    form_class = CurationCreateForm
    template_name = "curation/create.html"

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
    pk_url_kwarg = "curation_pk"


class CurationEdit(UpdateView):
    """Shows the user information about a curation."""

    model = Curation
    form_class = CurationEditForm
    template_name = "curation/edit_curation.html"
    pk_url_kwarg = "curation_pk"


@has_create_access
def curation_edit_evidence(request: HttpRequest, curation_pk: int) -> HttpResponse:
    """Returns the editable curation details page with editable top-level evidence.

    Args:
         request: The Django request object.
         curation_pk: The primary key for the curation.
    """
    curation = get_object_or_404(Curation, pk=curation_pk)
    evidence = Evidence.objects.filter(curation=curation)
    if request.method == "POST":
        evidence_formset = EvidenceTopLevelEditFormSet(request.POST, queryset=evidence)
        if evidence_formset.is_valid():
            evidence_formset.save()
            messages.success(request, "Changes saved successfully.")
            return redirect("curation-detail", curation_pk=curation.pk)
    else:
        evidence_formset = EvidenceTopLevelEditFormSet(queryset=evidence)

    context = {
        "curation": curation,
        "evidence_formset": evidence_formset,
    }
    return render(request, "curation/edit_evidence.html", context)


CURATION_TYPE_OPTIONS = [
    Filters.DEFAULT,
    CurationTypes.ALLELE,
    CurationTypes.HAPLOTYPE,
]

STATUS_OPTIONS = [
    Filters.DEFAULT,
    Status.IN_PROGRESS,
    Status.DONE,
]

FIELDS = [
    {
        "text": "ID",
        "param_name": "pk",
        "id": "pk",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Type",
        "param_name": "curation_type",
        "id": "curation-type",
        "default_value": CURATION_TYPE_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": CURATION_TYPE_OPTIONS,
    },
    {
        "text": "Allele",
        "param_name": "allele",
        "is_foreign_key": True,
        "filter": True,
        "id": "allele-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Haplotype",
        "param_name": "haplotype",
        "is_foreign_key": True,
        "id": "haplotype-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Disease",
        "param_name": "disease",
        "is_foreign_key": True,
        "id": "disease-name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Status",
        "param_name": "status",
        "id": "status",
        "default_value": STATUS_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": STATUS_OPTIONS,
    },
    {
        "text": "Added",
        "param_name": "added_at",
        "id": "added-at",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
]


def curation_search(request: HttpRequest) -> HttpResponse:
    """Returns an interactive datatable for searching curations."""
    return datatable(
        request=request,
        model=Curation,
        order_by="pk",
        fields=FIELDS,  # type: ignore
        data_title="Curations",
        partial="curation/partials/search.html",
    )


class EvidenceCreate(CreateAccessMixin, CreateView):  # type: ignore
    """Allows the user to create (add) evidence."""

    model = Evidence
    form_class = EvidenceCreateForm
    template_name = "evidence/create.html"

    def form_valid(self, form: EvidenceCreateForm) -> HttpResponse:
        """Makes sure the user who added the evidence is recorded.

        Returns:
             The details page for the evidence if the form is valid, or the form with
             errors otherwise.
        """
        curation = Curation.objects.get(pk=self.kwargs["curation_pk"])
        form.instance.curation = curation
        form.instance.added_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):  # noqa
        """Returns the context with the curation ID."""
        context = super().get_context_data(**kwargs)
        context["curation_pk"] = self.kwargs["curation_pk"]
        return context


FRAMEWORK = [
    {
        "text": "Step 1A: Allele or Haplotype",
        "category": "Allele",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1a",
        "points": Points.S1A_ALLELE,
        "operator": "+",
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "Haplotype",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1a",
        "points": Points.S1A_HAPLOTYPE,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 1B: Allele Resolution",
        "category": "1-field",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_1_FIELD,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 4,
    },
    {
        "text": None,
        "category": "2-field",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_2_FIELD,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": "3-field, G-group, P-group",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_3_FIELD,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": "4-field",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1b",
        "points": Points.S1B_4_FIELD,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": "Step 1C: Zygosity",
        "category": "Monoallelic (heterozygous)",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1c",
        "points": Points.S1C_MONOALLELIC,
        "operator": "+",
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "Biallelic (homozygous)",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1c",
        "points": Points.S1C_BIALLELIC,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 1D: Phase",
        "category": "Phase confirmed",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_1d",
        "points": Points.S1D_PHASE_CONFIRMED,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 1,
    },
    {
        "text": "Step 2: Typing Method",
        "category": "Tagging / Tag SNPs / Microarrays",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_TAG_SNPS,
        "operator": "+",
        "style": "white",
        "rowspan": 6,
    },
    {
        "text": None,
        "category": "Serological",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_SEROLOGICAL,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Imputation",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_IMPUTATION,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Molecular genotyping (low and high resolution) / Whole exome sequencing / RNA sequencing ",  # noqa: E501
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_LOW_RES_TYPING,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Sanger-sequencing-based typing / Whole gene sequencing",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_SANGER_SEQ,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": "Whole genome sequencing / Panel-based next generation sequencing (> 50x coverage) / Long-read sequencing",  # noqa: E501
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_2",
        "points": Points.S2_WHOLE_GENOME_SEQ,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 3A: Statistics (p-value)",
        "category": ["GWAS", "Non-GWAS"],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": "",
        "operator": "",
        "style": "whitesmoke",
        "rowspan": 6,
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_1, Intervals.S3A.NON_GWAS_1],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_1,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_2, Intervals.S3A.NON_GWAS_2],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_2,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_3, Intervals.S3A.NON_GWAS_3],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_3,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_4, Intervals.S3A.NON_GWAS_4],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_4,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": None,
        "category": [Intervals.S3A.GWAS_5, Intervals.S3A.NON_GWAS_5],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_3a",
        "points": Points.S3A_INTERVAL_5,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": "Step 3B: Multiple Testing Correction",
        "category": "Overall correction for multiple testing",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_3b",
        "points": Points.S3B_OVERALL,
        "operator": "+",
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "2-step p-value correction",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_3b",
        "points": Points.S3B_TWO_STEP,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 3C: Statistics (Effect Size)*",
        "category": [
            Intervals.S3C.OR_RR_1,
            Intervals.S3C.OR_RR_2,
            Intervals.S3C.BETA_1,
            Intervals.S3C.BETA_2,
        ],
        "split_horizontal": False,
        "split_vertical": True,
        "score": "score_step_3c1",
        "points": Points.S3C_OR_RR_BETA,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "CI does not cross 1 (OR/RR) or 0 (beta)",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_3c2",
        "points": Points.S3C_CI_DOES_NOT_CROSS,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "text": "Step 4: Cohort Size",
        "category": ["GWAS", "Non-GWAS"],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": "",
        "operator": "",
        "style": "white",
        "rowspan": 6,
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_1, Intervals.S4.NON_GWAS_1],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_1,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_2, Intervals.S4.NON_GWAS_2],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_2,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_3, Intervals.S4.NON_GWAS_3],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_3,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_4, Intervals.S4.NON_GWAS_4],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_4,
        "operator": "+",
        "style": "white",
    },
    {
        "text": None,
        "category": [Intervals.S4.GWAS_5, Intervals.S4.NON_GWAS_5],
        "split_horizontal": True,
        "split_vertical": False,
        "score": "score_step_4",
        "points": Points.S4_INTERVAL_5,
        "operator": "+",
        "style": "white",
    },
    {
        "text": "Step 5: Additional Phenotypes",
        "category": "Has specific disease-related phenotype",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_5",
        "points": Points.S5_SPECIFIC_PHENOTYPE,
        "operator": "+",
        "style": "whitesmoke",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "Only disease tested",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_5",
        "points": Points.S5_ONLY_DISEASE_TESTED,
        "operator": "+",
        "style": "whitesmoke",
    },
    {
        "is_total_row": True,
        "score": "score_before_multipliers",
        "text": "Total Before Multipliers",
        "style": "lightblue",
        "id": "total-score-before-multipliers",
    },
    {
        "text": "Step 6A: Weighing Association (multiplier)",
        "category": "Significant association with disease",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6a",
        "points": Points.S6A_ASSOCIATION,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "white",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "No significant association",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6a",
        "points": Points.S6A_NO_ASSOCIATION,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "white",
    },
    {
        "text": "Step 6B: Low Field Resolution (multiplier)",
        "category": "1-field resolution",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6b",
        "points": Points.S6B_1_FIELD,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "whitesmoke",
        "rowspan": 2,
    },
    {
        "text": None,
        "category": "> 1-field resolution",
        "split_horizontal": False,
        "split_vertical": False,
        "score": "score_step_6b",
        "points": Points.S6B_MORE_THAN_1_FIELD,
        "operator": "×",  # noqa: RUF001 (I want a multiplication sign here.)
        "style": "whitesmoke",
    },
    {
        "is_total_row": True,
        "score": "score",
        "text": "Total",
        "style": "lightblue",
        "id": "total-score",
    },
]


class EvidenceDetail(DetailView):
    """Shows the user information about evidence."""

    model = Evidence
    template_name = "evidence/detail.html"
    pk_url_kwarg = "evidence_pk"

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
    pk_url_kwarg = "evidence_pk"

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
        effect_size_statistic = form.cleaned_data["effect_size_statistic"]
        if effect_size_statistic == EffectSizeStatistic.ODDS_RATIO:
            form.instance.relative_risk_string = ""
            form.instance.relative_risk = None
            form.instance.beta_string = ""
            form.instance.beta = None
        elif effect_size_statistic == EffectSizeStatistic.RELATIVE_RISK:
            form.instance.odds_ratio_string = ""
            form.instance.odds_ratio = None
            form.instance.beta_string = ""
            form.instance.beta = None
        elif effect_size_statistic == EffectSizeStatistic.BETA:
            form.instance.relative_risk_string = ""
            form.instance.relative_risk = None
            form.instance.odds_ratio_string = ""
            form.instance.odds_ratio = None

        p_value_string = form.cleaned_data["p_value_string"]
        if p_value_string == "":
            form.instance.p_value = None
        else:
            form.instance.p_value = Decimal(p_value_string)

        odds_ratio_string = form.cleaned_data["odds_ratio_string"]
        if odds_ratio_string == "":
            form.instance.odds_ratio = None
        else:
            form.instance.odds_ratio = Decimal(odds_ratio_string)

        relative_risk_string = form.cleaned_data["relative_risk_string"]
        if relative_risk_string == "":
            form.instance.relative_risk = None
        else:
            form.instance.relative_risk = Decimal(relative_risk_string)

        beta_string = form.cleaned_data["beta_string"]
        if beta_string == "":
            form.instance.beta = None
        else:
            form.instance.beta = Decimal(beta_string)

        ci_start_string = form.cleaned_data["ci_start_string"]
        if ci_start_string == "":
            form.instance.ci_start = None
        else:
            form.instance.ci_start = Decimal(ci_start_string)

        ci_end_string = form.cleaned_data["ci_end_string"]
        if ci_end_string == "":
            form.instance.ci_end = None
        else:
            form.instance.ci_end = Decimal(ci_end_string)

        return super().form_valid(form)
