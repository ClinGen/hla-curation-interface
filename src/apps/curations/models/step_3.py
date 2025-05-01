"""Provide a model for the question asked in step 3."""

from django.db import models


class Step3(models.Model):
    """This model represents the question asked in step 3.

    We're trying to capture the p-value in scientific notation:
        m x 10^n

    In the above expression:
        - m is the significand
        - n is the exponent
    """

    is_gwas = models.BooleanField(
        verbose_name="Is GWAS?", help_text="Is this a GWAS result?"
    )
    significand = models.FloatField(
        verbose_name="Significand", help_text="The significand of the p-value."
    )
    exponent = models.IntegerField(
        verbose_name="Exponent", help_text="The exponent of the p-value."
    )

    def __str__(self) -> str:
        """Return a string representation of the model."""
        return f"GWAS: {self.is_gwas}, p-value: {self.significand} x 10^{self.exponent}"
