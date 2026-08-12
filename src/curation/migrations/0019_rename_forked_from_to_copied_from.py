from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("curation", "0018_remove_timestamp_fields_fix_disease_null"),
    ]

    operations = [
        migrations.RenameField(
            model_name="curation",
            old_name="forked_from",
            new_name="copied_from",
        ),
        migrations.RenameField(
            model_name="historicalcuration",
            old_name="forked_from",
            new_name="copied_from",
        ),
    ]
