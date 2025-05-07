"""Configures the admin page for the `AlleleCuration` model."""

from django.contrib import admin

from apps.curations.models.allele import AlleleCuration

admin.site.register(AlleleCuration)
