from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from allele.clients import fetch_allele_data, get_car_id
from allele.forms import AlleleForm
from allele.models import Allele
from auth_.permissions import ProtectedViewMixin


class AlleleCreate(ProtectedViewMixin, CreateView):  # type: ignore
    model = Allele
    form_class = AlleleForm
    template_name = "allele/create.html"
    success_url = reverse_lazy("allele-list")

    def form_valid(self, form: AlleleForm) -> HttpResponse:
        """Fetches and adds data from the ClinGen Allele Registry and records user.

        Returns:
             The success page for the allele if the form is valid, or the form with
             errors if the form isn't valid.
        """
        allele_data = fetch_allele_data(form.instance.name)
        if allele_data:
            form.instance.car_id = get_car_id(allele_data)
            form.instance.added_by = self.request.user
            messages.success(self.request, "Added allele.")
            return super().form_valid(form)
        message = (
            "Oops, something went wrong trying to fetch data from the "
            "ClinGen Allele Registry. Please try again later."
        )
        messages.warning(self.request, message)
        return redirect("allele-create")


class AlleleDetail(ProtectedViewMixin, DetailView):  # type: ignore
    model = Allele
    template_name = "allele/detail.html"


class AlleleList(ProtectedViewMixin, ListView):  # type: ignore
    model = Allele
    template_name = "allele/list.html"
