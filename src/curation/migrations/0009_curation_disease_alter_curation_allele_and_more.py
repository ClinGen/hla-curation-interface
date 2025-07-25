# Generated by Django 5.2.1 on 2025-07-12 23:41

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("allele", "0004_alter_allele_name"),
        ("curation", "0008_alter_evidence_options_alter_evidence_table"),
        ("disease", "0004_remove_disease_ols_iri_disease_iri"),
        ("haplotype", "0002_alter_haplotype_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="curation",
            name="disease",
            field=models.ForeignKey(
                blank=True,
                help_text="Select the disease for this curation.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="curations",
                to="disease.disease",
            ),
        ),
        migrations.AlterField(
            model_name="curation",
            name="allele",
            field=models.ForeignKey(
                blank=True,
                help_text="Select the allele for this curation.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="curations",
                to="allele.allele",
            ),
        ),
        migrations.AlterField(
            model_name="curation",
            name="haplotype",
            field=models.ForeignKey(
                blank=True,
                help_text="Select the haplotype for this curation.",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="curations",
                to="haplotype.haplotype",
            ),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="status",
            field=models.CharField(
                choices=[("INP", "In Progress"), ("DNE", "Done")],
                default="INP",
                help_text="Either 'INP' (in progress) or 'DNE' (done).",
                max_length=3,
                verbose_name="Status",
            ),
        ),
    ]
