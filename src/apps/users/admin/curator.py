"""Configure the admin page for the curator model."""

from django.contrib import admin

from apps.users.models.curator import Curator

admin.site.register(Curator)
