"""Configure the admin page for the `Curation` model."""

from django.contrib import admin

from apps.curations.models.allele import AlleleCuration

admin.site.register(AlleleCuration)
