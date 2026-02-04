"""Configures URLs for the allele app."""

from django.urls import path

from allele import views
from allele.views import AlleleList

urlpatterns = [
    path("create", views.AlleleCreate.as_view(), name="allele-create"),
    path("<slug:slug>/detail", views.AlleleDetail.as_view(), name="allele-detail"),
    path("search", views.allele_search, name="allele-search"),
    path("list", AlleleList.as_view(), name="allele-list"),
]
