"""Configure the admin page for the allele model."""

from django.contrib import admin

from apps.diseases.models.mondo import Mondo

admin.site.register(Mondo)
