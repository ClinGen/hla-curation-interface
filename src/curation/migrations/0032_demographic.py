# Generated by Django 5.2.1 on 2025-07-18 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curation", "0031_evidence_has_association_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Demographic",
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
                    "group",
                    models.CharField(
                        choices=[
                            ("AME", "American"),
                            ("EAS", "East Asian"),
                            ("EUR", "European"),
                            ("SAS", "Central/South Asian"),
                            ("NEA", "Near Eastern"),
                            ("OCE", "Oceanian"),
                            ("SSA", "Sub-Saharan African"),
                        ],
                        help_text="The code for the bio-geographical group.",
                        max_length=3,
                        unique=True,
                        verbose_name="Group",
                    ),
                ),
            ],
            options={
                "verbose_name": "Demographic",
                "verbose_name_plural": "Demographics",
                "db_table": "demographic",
            },
        ),
    ]
