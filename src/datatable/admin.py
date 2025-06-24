"""Configures the admin site for the datatable app."""

from django.contrib import admin

from datatable.models import Pokemon

admin.site.register(Pokemon)
