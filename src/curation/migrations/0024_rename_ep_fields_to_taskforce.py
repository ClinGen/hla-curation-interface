from django.db import migrations

RENAMES = [
    ("ep", "taskforce"),
    ("ep_additional_notes", "taskforce_additional_notes"),
    ("ep_classification", "taskforce_classification"),
    ("ep_evidence_summary", "taskforce_evidence_summary"),
    ("ep_override_reason", "taskforce_override_reason"),
    ("ep_review_date", "taskforce_review_date"),
]


class Migration(migrations.Migration):
    dependencies = [
        ("curation", "0023_add_curation_ep_override_reason"),
    ]

    operations = [
        migrations.RenameField(model_name=model, old_name=old, new_name=new)
        for model in ("curation", "historicalcuration")
        for old, new in RENAMES
    ]
