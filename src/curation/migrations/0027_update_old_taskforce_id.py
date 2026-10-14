"""Moves curations from the old HLA Curation Taskforce ID to the new one.

1a39f48 changed HLA_CURATION_TASKFORCE_ID from 40033 to 10144 but left the stored
rows alone, so curations reviewed before then still show the bare old ID.
Historical rows are mapped too, so history views agree with the current rows.

Going backward does nothing: a row that holds 10144 might have been saved with the
new ID, and there's no way to tell it from one this migration changed.
"""

from django.db import migrations

OLD_ID = "40033"
NEW_ID = "10144"
MODELS = ["Curation", "HistoricalCuration"]


def update_taskforce_id(apps, schema_editor):
    """Maps the old taskforce ID to the new one.

    Args:
        apps: The app registry for the migration state.
        schema_editor: The schema editor (unused).
    """
    for model_name in MODELS:
        model = apps.get_model("curation", model_name)
        model.objects.filter(taskforce=OLD_ID).update(taskforce=NEW_ID)


class Migration(migrations.Migration):

    dependencies = [
        ("curation", "0026_fix_zygosity_help_text"),
    ]

    operations = [
        migrations.RunPython(update_taskforce_id, reverse_code=migrations.RunPython.noop),
    ]
