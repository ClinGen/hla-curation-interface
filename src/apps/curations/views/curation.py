"""Provide a view for editing a curation."""

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from apps.curations.forms.step_1 import Step1Form
from apps.curations.forms.step_2 import Step2Form
from apps.curations.forms.step_3 import Step3Form


def edit(request: HttpRequest) -> HttpResponse:
    """Return the edit curation forms."""
    step_1_form = Step1Form()
    step_2_form = Step2Form()
    step_3_form = Step3Form()
    if request.method == "POST":
        if "step_1" in request.POST:
            step_1_form = Step1Form(request.POST)
            if step_1_form.is_valid():
                step_1_form.save()
        if "step_2" in request.POST:
            step_2_form = Step2Form(request.POST)
            if step_2_form.is_valid():
                step_2_form.save()
        if "step_3" in request.POST:
            step_3_form = Step3Form(request.POST)
            if step_3_form.is_valid():
                step_3_form.save()
    else:
        step_1_form = Step1Form()
        step_2_form = Step2Form()
        step_3_form = Step3Form()
    context = {
        "step_1_form": step_1_form,
        "step_2_form": step_2_form,
        "step_3_form": step_3_form,
    }
    return render(request, "curations/allele/edit.html", context)
