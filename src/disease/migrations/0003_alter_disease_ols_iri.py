# Generated by Django 5.2.1 on 2025-06-26 21:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("disease", "0002_disease_ols_iri_alter_disease_disease_type_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="disease",
            name="ols_iri",
            field=models.CharField(
                blank=True,
                default="",
                max_length=88,
                verbose_name="Ontology Lookup Service (OLS) Internationalized Resource Identifier (IRI)",
            ),
        ),
    ]
