from collections.abc import Iterable

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.http import HttpResponseBase
from django.urls import reverse
from simple_history.models import HistoricalRecords

from allele.models import Allele
from haplotype.constants.models import GENE_LIST


class Haplotype(models.Model):
    slug = models.SlugField(
        default="",
        max_length=7,
        verbose_name="Human-Readable ID",
        help_text="The human-readable ID for the object.",
    )
    alleles = models.ManyToManyField(
        Allele,
        blank=False,
        db_table="haplotype_allele_map",
        related_name="haplotypes",
        help_text="The constituent alleles of the haplotype.",
    )
    name = models.CharField(
        blank=False,
        default="",
        max_length=240,  # Should be plenty of characters.
        unique=True,
        verbose_name="Name",
        help_text=(
            "The name of the HLA haplotype, e.g., DRB1*15:01~DQB1*06:02. "
            "(The 'HLA-' part should be omitted.)"
        ),
    )
    added_by = models.ForeignKey(
        User,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name="haplotypes_added",
        verbose_name="Added By",
        help_text="The user who added the haplotype.",
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Added At",
        help_text="When the haplotype was added.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Updated At",
        help_text="When the haplotype was last updated.",
    )
    history = HistoricalRecords()

    class Meta:
        db_table = "haplotype"
        verbose_name = "Haplotype"
        verbose_name_plural = "Haplotypes"

    def __str__(self) -> str:
        return self.display_name

    def save(self, *args, **kwargs) -> None:
        super().save(*args, **kwargs)
        if not self.slug:
            self.slug = f"H{self.pk:06d}"
            self.save(update_fields=["slug"])

    def get_absolute_url(self) -> HttpResponseBase | str | None:
        return reverse("haplotype-detail", kwargs={"slug": self.slug})

    @staticmethod
    def canonical_name(allele_names: Iterable[str]) -> str:
        """Joins allele names with '~' in the order of their genes on chromosome 6.

        Args:
            allele_names: The constituent allele names, in any order.

        Returns:
            The haplotype name, e.g., DRB1*15:01~DQB1*06:02.

        Raises:
            ValidationError: If an allele's gene isn't in GENE_LIST.
        """
        genes = {name: name.split("*")[0] for name in allele_names}
        unknown = [name for name, gene in genes.items() if gene not in GENE_LIST]
        if unknown:
            raise ValidationError({"name": f"{unknown[0]} has an unknown gene."})
        return "~".join(sorted(genes, key=lambda name: GENE_LIST.index(genes[name])))

    @classmethod
    def get_or_build(cls, name: str) -> tuple["Haplotype", list[Allele]]:
        """Returns the haplotype with the name, or builds an unsaved one.

        Args:
            name: The constituent allele names joined by '~', in any order.

        Returns:
            The existing or new unsaved haplotype, and its alleles in canonical
            order. Alleles that aren't in the database are fetched and unsaved, so
            the caller saves them, saves the haplotype, then adds the alleles.

        Raises:
            ValidationError: If the name is malformed, has an unknown gene, or an
                allele can't be fetched from the ClinGen Allele Registry.
        """
        allele_names = [part.strip() for part in name.split("~")]
        if not all(allele_names):
            raise ValidationError(
                {"name": "Separate allele names with '~', e.g., A*01:01~B*08:01."}
            )
        canonical_name = cls.canonical_name(allele_names)
        haplotype = cls.objects.filter(name=canonical_name).first()
        alleles = [Allele.get_or_build(part) for part in canonical_name.split("~")]
        return haplotype or cls(name=canonical_name), alleles

    @property
    def display_name(self) -> str:
        return "~".join(f"HLA-{part}" for part in self.name.split("~"))
