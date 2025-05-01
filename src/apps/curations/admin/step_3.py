"""Configure the admin page for the step 3 model."""

from django.contrib import admin

from apps.curations.models.step_3 import Step3

admin.site.register(Step3)
