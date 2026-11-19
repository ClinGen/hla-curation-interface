from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from django.urls import reverse
from django.utils.html import format_html

from allele.models import Allele
from common.widgets import SuggestInput
from haplotype.constants.forms import TYPED_HAPLOTYPE_HELP_TEXT
from haplotype.constants.models import ALLELE_SEPARATORS, HAPLOTYPE_NAME_SEPARATOR
from haplotype.models import Haplotype


class HaplotypeForm(ModelForm):
    alleles = forms.CharField(
        label="Alleles",
        help_text=TYPED_HAPLOTYPE_HELP_TEXT,
        widget=SuggestInput("allele-suggest", separators=ALLELE_SEPARATORS),
    )

    class Meta:
        model = Haplotype
        fields: list[str] = []

    def clean_alleles(self) -> list[Allele]:
        """Looks up the typed alleles and names the haplotype after them.

        Only alleles already in the HCI are used; nothing is fetched.

        Returns:
            The alleles in canonical order.

        Raises:
            ValidationError: If an allele isn't in the HCI, a gene is unknown, or
                the haplotype already exists.
        """
        typed = ALLELE_SEPARATORS.split(self.cleaned_data["alleles"])
        names = [name for name in typed if name]
        alleles = Allele.objects.filter(name__in=names)
        found = {allele.name: allele for allele in alleles}
        missing = [name for name in names if name not in found]
        if missing:
            message = format_html(
                '{} isn\'t in the HCI. <a href="{}">Add the allele</a> first.',
                missing[0],
                reverse("allele-create"),
            )
            raise ValidationError(message)
        try:
            name = Haplotype.canonical_name(names)
        except ValidationError as error:
            raise ValidationError(error.messages) from error
        if Haplotype.objects.filter(name=name).exists():
            message = "A haplotype with these alleles already exists."
            raise ValidationError(message)
        self.instance.name = name
        parts = name.split(HAPLOTYPE_NAME_SEPARATOR)
        return [found[allele_name] for allele_name in parts]

    def save(self, *args, **kwargs) -> Haplotype:
        """Saves the haplotype, then links its alleles.

        Returns:
            The haplotype.
        """
        haplotype = super().save(*args, **kwargs)
        haplotype.alleles.add(*self.cleaned_data["alleles"])
        return haplotype
