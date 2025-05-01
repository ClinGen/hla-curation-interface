"""Configure the admin page for the affiliation model."""

from django.contrib import admin

from apps.users.models.affiliation import Affiliation

admin.site.register(Affiliation)
