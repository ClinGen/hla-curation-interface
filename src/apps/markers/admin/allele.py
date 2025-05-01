"""Configure the admin page for the allele model."""

from django.contrib import admin

from apps.markers.models.allele import Allele

admin.site.register(Allele)
