"""Configures URLs."""

from django.urls import path

from datatable import views

urlpatterns = [path("pokemon", views.pokemon, name="pokemon")]
