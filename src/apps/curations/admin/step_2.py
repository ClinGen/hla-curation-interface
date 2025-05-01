"""Configure the admin page for the step 2 model."""

from django.contrib import admin

from apps.curations.models.step_2 import Step2

admin.site.register(Step2)
