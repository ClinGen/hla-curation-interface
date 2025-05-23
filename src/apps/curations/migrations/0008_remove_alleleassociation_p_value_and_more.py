# Generated by Django 5.2 on 2025-05-12 23:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "curations",
            "0007_alleleassociation_is_gwas_alleleassociation_p_value_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="alleleassociation",
            name="p_value",
        ),
        migrations.AddField(
            model_name="alleleassociation",
            name="p_value_number",
            field=models.DecimalField(
                blank=True,
                decimal_places=30,
                default=None,
                help_text="The p-value as a decimal.",
                max_digits=31,
                null=True,
                verbose_name="p-value as a number",
            ),
        ),
        migrations.AddField(
            model_name="alleleassociation",
            name="p_value_text",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The p-value as a decimal or in scientific notation, e.g., 5e-8.",
                null=True,
                verbose_name="p-value",
            ),
        ),
    ]
