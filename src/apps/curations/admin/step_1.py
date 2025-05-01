"""Configure the admin page for the step 1 model."""

from django.contrib import admin

from apps.curations.models.step_1 import Step1

admin.site.register(Step1)
