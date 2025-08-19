"""Configures URLs for the allele app."""

from django.urls import path

from allele import views

urlpatterns = [
    path("create", views.AlleleCreate.as_view(), name="allele-create"),
    path("<int:pk>/detail", views.AlleleDetail.as_view(), name="allele-detail"),
    path("search", views.allele_search, name="allele-search"),
]
