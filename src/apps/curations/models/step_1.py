"""Provide a model for the questions asked in step 1."""

from django.db import models

STEP_1A_CHOICES = {
    "AL": "Allele",
    "HA": "Haplotype",
}

STEP_1B_CHOICES = {
    "1F": "1-field",
    "2F": "2-field",
    "3F": "3-field",
    "GG": "G-group",
    "PG": "P-group",
    "4F": "4-field",
}

STEP_1C_CHOICES = {
    "MO": "Monoallelic (heterozygous)",
    "BI": "Biallelic (homozygous)",
}


class Step1(models.Model):
    """This model represents the questions asked in step 1."""

    step_1a_marker_type = models.CharField(
        choices=STEP_1A_CHOICES,
        max_length=2,
        verbose_name="Marker Type",
        help_text="Is the study about an allele or a haplotype?",
    )
    step_1b_allele_resolution = models.CharField(
        choices=STEP_1B_CHOICES,
        max_length=2,
        verbose_name="Allele Resolution",
        help_text="What is the allele resolution?",
    )
    step_1c_zygosity = models.CharField(
        choices=STEP_1C_CHOICES,
        max_length=2,
        verbose_name="Zygosity",
        help_text="What is the zygosity?",
    )
    step_1d_phase_is_confirmed = models.BooleanField(
        verbose_name="Phase is confirmed?", help_text="Is the phase confirmed?"
    )

    def __str__(self) -> str:
        """Return a string representation of the answers to the questions."""
        marker_type = f"Marker Type: {self.step_1a_marker_type}"
        allele_resolution = f"Allele Resolution: {self.step_1b_allele_resolution}"
        zygosity = f"Zygosity: {self.step_1c_zygosity}"
        phase_is_confirmed = f"Phase is confirmed? {self.step_1d_phase_is_confirmed}"
        return f"{marker_type}, {allele_resolution}, {zygosity}, {phase_is_confirmed}"
