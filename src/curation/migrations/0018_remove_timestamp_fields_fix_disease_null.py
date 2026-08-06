import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("curation", "0017_add_curation_published_at"),
        ("disease", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(model_name="curation", name="in_progress_at"),
        migrations.RemoveField(model_name="curation", name="ready_for_review_at"),
        migrations.RemoveField(model_name="curation", name="provisional_at"),
        migrations.RemoveField(model_name="curation", name="published_at"),
        migrations.RemoveField(model_name="historicalcuration", name="in_progress_at"),
        migrations.RemoveField(model_name="historicalcuration", name="ready_for_review_at"),
        migrations.RemoveField(model_name="historicalcuration", name="provisional_at"),
        migrations.RemoveField(model_name="historicalcuration", name="published_at"),
        migrations.AlterField(
            model_name="curation",
            name="disease",
            field=models.ForeignKey(
                help_text="Select the disease for this curation.",
                on_delete=django.db.models.deletion.CASCADE,
                related_name="curations",
                to="disease.disease",
            ),
        ),
    ]
