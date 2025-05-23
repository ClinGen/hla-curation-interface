# Generated by Django 5.2 on 2025-05-13 04:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curations", "0011_alleleassociation_odds_ratio"),
    ]

    operations = [
        migrations.AddField(
            model_name="alleleassociation",
            name="beta",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The beta as a decimal number, e.g., 0.73.",
                null=True,
                verbose_name="Beta",
            ),
        ),
        migrations.AddField(
            model_name="alleleassociation",
            name="confidence_interval_end",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The relative risk as a decimal number, e.g., 0.38.",
                null=True,
                verbose_name="End of the Confidence Interval",
            ),
        ),
        migrations.AddField(
            model_name="alleleassociation",
            name="confidence_interval_start",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The relative risk as a decimal number, e.g., 0.001.",
                null=True,
                verbose_name="Start of the Confidence Interval",
            ),
        ),
        migrations.AddField(
            model_name="alleleassociation",
            name="relative_risk",
            field=models.CharField(
                blank=True,
                default=None,
                help_text="The relative risk as a decimal number, e.g., 0.73.",
                null=True,
                verbose_name="Relative Risk",
            ),
        ),
    ]
