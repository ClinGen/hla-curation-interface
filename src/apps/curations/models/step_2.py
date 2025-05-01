"""Provide a model for the question asked in step 2."""

from django.db import models

STEP_2_CHOICES = {
    "TSM": "Tag SNPs or Microarrays",
    "SER": "Serological",
    "IMP": "Imputation",
    "LRT": "Low-Resolution Typing",
    "HRT": "High-Resolution Typing",
    "WES": "Whole-Exome Sequencing",
    "SST": "Sanger Sequencing-Based Typing",
    "WGS": "Whole-Gene Sequencing",
    "NGS": "Whole Genome Sequencing and/or Panel-Based NGS (>50x coverage)",
}


class Step2(models.Model):
    """This model represents the question asked in step 2."""

    step_2_typing_method = models.CharField(
        choices=STEP_2_CHOICES,
        max_length=3,
        verbose_name="Typing Method",
        help_text="What method was used to determine the typing?",
    )

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"Typing Method: {self.step_2_typing_method}"
