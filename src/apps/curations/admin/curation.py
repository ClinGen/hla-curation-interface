"""Configure the admin page for the `Curation` model."""

from django.contrib import admin

from apps.curations.models.curation import Curation

admin.site.register(Curation)
