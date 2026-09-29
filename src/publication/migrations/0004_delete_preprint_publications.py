"""Deletes bioRxiv and medRxiv publications.

Curators can only add PubMed articles, so preprint publications are legacy data. None
were expected in the test or production databases when this was written.
"""

from django.db import migrations

PREPRINT_TYPES = ["BIO", "MED"]


def delete_preprint_publications(apps, schema_editor):
    """Deletes preprint publications, unless evidence cites them.

    Evidence.publication cascades on delete, so deleting a cited preprint would also
    delete its evidence. Raising instead rolls back the migration so someone can look
    at the evidence first.

    Args:
        apps: The app registry for the migration state.
        schema_editor: The schema editor (unused).

    Raises:
        RuntimeError: If any evidence cites a preprint publication.
    """
    publication_model = apps.get_model("publication", "Publication")
    evidence_model = apps.get_model("curation", "Evidence")
    preprints = publication_model.objects.filter(publication_type__in=PREPRINT_TYPES)
    cited_slugs = sorted(
        set(
            evidence_model.objects.filter(publication__in=preprints).values_list(
                "publication__slug", flat=True
            )
        )
    )
    if cited_slugs:
        message = (
            "Evidence cites these preprint publications, so they were not deleted: "
            f"{', '.join(cited_slugs)}"
        )
        raise RuntimeError(message)
    preprints.delete()


class Migration(migrations.Migration):
    dependencies = [
        ("publication", "0003_historicalpublication"),
        ("curation", "0020_alter_curation_copied_from_and_more"),
    ]

    operations = [
        migrations.RunPython(
            delete_preprint_publications, reverse_code=migrations.RunPython.noop
        ),
    ]
