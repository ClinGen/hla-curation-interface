"""Provide a model for an association."""

from django.db import models

from apps.curations.models.step_1 import Step1
from apps.curations.models.step_2 import Step2
from apps.curations.models.step_3 import Step3


class Association(models.Model):
    """This model represents an association."""

    step_1: models.OneToOneField = models.OneToOneField(Step1, on_delete=models.CASCADE)
    step_2: models.OneToOneField = models.OneToOneField(Step2, on_delete=models.CASCADE)
    step_3: models.OneToOneField = models.OneToOneField(Step3, on_delete=models.CASCADE)

    def __str__(self) -> str:
        """Return a string representation of the association."""
        return "Association <human readable ID here>"
