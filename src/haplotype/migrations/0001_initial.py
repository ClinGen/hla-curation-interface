# Generated by Django 5.2.1 on 2025-07-06 05:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("allele", "0004_alter_allele_name"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Haplotype",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        default="",
                        help_text="The name of the HLA haplotype, e.g., DRB1*15:01~DQB1*06:02. (The 'HLA-' part should be omitted.)",
                        max_length=300,
                        unique=True,
                        verbose_name="Name",
                    ),
                ),
                (
                    "added_at",
                    models.DateTimeField(
                        auto_now_add=True,
                        help_text="When the haplotype was added.",
                        verbose_name="Added At",
                    ),
                ),
                (
                    "added_by",
                    models.ForeignKey(
                        blank=True,
                        help_text="The user who added the haplotype.",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="haplotypes_added",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Added By",
                    ),
                ),
                (
                    "alleles",
                    models.ManyToManyField(
                        db_table="haplotype_allele_map",
                        help_text="The constituent alleles of the haplotype.",
                        related_name="haplotypes",
                        to="allele.allele",
                    ),
                ),
            ],
            options={
                "verbose_name": "Haplotype",
                "verbose_name_plural": "Haplotypes",
                "db_table": "haplotype",
            },
        ),
    ]
