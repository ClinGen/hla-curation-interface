"""Configures the admin page for the `AlleleCuration` model."""

from django.contrib import admin

from apps.curations.models.allele.association import PubMedAlleleAssociation
from apps.curations.models.allele.curation import AlleleCuration

admin.site.register(PubMedAlleleAssociation)
admin.site.register(AlleleCuration)
