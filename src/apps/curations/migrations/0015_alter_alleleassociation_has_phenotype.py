# Generated by Django 5.2 on 2025-05-13 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curations", "0014_alleleassociation_has_phenotype"),
    ]

    operations = [
        migrations.AlterField(
            model_name="alleleassociation",
            name="has_phenotype",
            field=models.BooleanField(
                choices=[
                    (True, "Has disease-related phenotype"),
                    (False, "Only disease tested"),
                ],
                default=True,
                max_length=1,
                verbose_name="Has Disease-Related Phenotype",
            ),
        ),
    ]
