"""Renames the curation status codes for review.

Ready for Review (RFR) becomes Provisional (PRV), and Provisional (PRO) becomes
Approved (APR). The codes change, not just the labels, so PRO never means two things.
Historical rows are mapped too, so history views keep showing the right labels.

This also picks up the Evidence.num_fields label changes from f85bc1d, which had no
migration.
"""

from django.db import migrations, models

FORWARD = {"RFR": "PRV", "PRO": "APR"}
BACKWARD = {new: old for old, new in FORWARD.items()}
MODELS = ["Curation", "HistoricalCuration"]


def _map_statuses(apps, mapping):
    for model_name in MODELS:
        model = apps.get_model("curation", model_name)
        for old, new in mapping.items():
            model.objects.filter(status=old).update(status=new)


def rename_status_codes(apps, schema_editor):
    """Maps RFR to PRV and PRO to APR.

    Args:
        apps: The app registry for the migration state.
        schema_editor: The schema editor (unused).
    """
    _map_statuses(apps, FORWARD)


def restore_status_codes(apps, schema_editor):
    """Maps PRV back to RFR and APR back to PRO.

    Args:
        apps: The app registry for the migration state.
        schema_editor: The schema editor (unused).
    """
    _map_statuses(apps, BACKWARD)


class Migration(migrations.Migration):

    dependencies = [
        ("curation", "0020_alter_curation_copied_from_and_more"),
    ]

    operations = [
        migrations.RunPython(rename_status_codes, reverse_code=restore_status_codes),
        migrations.AlterField(
            model_name="curation",
            name="status",
            field=models.CharField(
                choices=[
                    ("INP", "In Progress"),
                    ("PRV", "Provisional"),
                    ("APR", "Approved"),
                    ("PUB", "Published"),
                ],
                default="INP",
                help_text="The current lifecycle status of the curation.",
                max_length=3,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="num_fields",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "1-Field"),
                    (2, "2-Field, P-Group"),
                    (3, "3-Field, G-Group"),
                    (4, "4-Field"),
                ],
                help_text="The allele resolution (number of fields) for the allele or haplotype in the study.",
                null=True,
                verbose_name="Number of Fields",
            ),
        ),
        migrations.AlterField(
            model_name="historicalcuration",
            name="status",
            field=models.CharField(
                choices=[
                    ("INP", "In Progress"),
                    ("PRV", "Provisional"),
                    ("APR", "Approved"),
                    ("PUB", "Published"),
                ],
                default="INP",
                help_text="The current lifecycle status of the curation.",
                max_length=3,
                verbose_name="Status",
            ),
        ),
        migrations.AlterField(
            model_name="historicalevidence",
            name="num_fields",
            field=models.IntegerField(
                blank=True,
                choices=[
                    (1, "1-Field"),
                    (2, "2-Field, P-Group"),
                    (3, "3-Field, G-Group"),
                    (4, "4-Field"),
                ],
                help_text="The allele resolution (number of fields) for the allele or haplotype in the study.",
                null=True,
                verbose_name="Number of Fields",
            ),
        ),
    ]
