"""Tests for the publication app's data migrations."""

from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

CURATION = ("curation", "0020_alter_curation_copied_from_and_more")
BEFORE = [("publication", "0003_historicalpublication"), CURATION]
AFTER = [("publication", "0004_delete_preprint_publications"), CURATION]


class DeletePreprintPublicationsTest(TransactionTestCase):
    """Runs 0004_delete_preprint_publications against the migration state before it.

    The current Publication model has no publication_type field, so these tests create
    rows with the historical models instead.
    """

    def setUp(self):
        executor = MigrationExecutor(connection)
        executor.migrate(BEFORE)
        apps = executor.loader.project_state(BEFORE).apps
        self.publication_model = apps.get_model("publication", "Publication")
        self.evidence_model = apps.get_model("curation", "Evidence")
        self.curation_model = apps.get_model("curation", "Curation")
        self.disease_model = apps.get_model("disease", "Disease")
        self.publication_model.objects.create(
            slug="P000001", publication_type="PUB", pubmed_id="123"
        )
        self.biorxiv = self.publication_model.objects.create(
            slug="P000002", publication_type="BIO", doi="10.1101/456"
        )
        self.publication_model.objects.create(
            slug="P000003", publication_type="MED", doi="10.1101/789"
        )

    def tearDown(self):
        # Otherwise, migrating forward fails when a test leaves evidence on a preprint.
        self.evidence_model.objects.all().delete()
        executor = MigrationExecutor(connection)
        executor.migrate(executor.loader.graph.leaf_nodes())

    def migrate_forward(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(AFTER)
        return executor.loader.project_state(AFTER).apps

    def test_deletes_preprints_and_keeps_pubmed_publications(self):
        apps = self.migrate_forward()
        publication_model = apps.get_model("publication", "Publication")
        self.assertEqual(
            list(publication_model.objects.values_list("publication_type", flat=True)),
            ["PUB"],
        )

    def test_raises_and_deletes_nothing_when_evidence_cites_a_preprint(self):
        disease = self.disease_model.objects.create(mondo_id="MONDO:123")
        curation = self.curation_model.objects.create(disease=disease)
        self.evidence_model.objects.create(curation=curation, publication=self.biorxiv)
        with self.assertRaisesMessage(RuntimeError, "P000002"):
            self.migrate_forward()
        self.assertEqual(self.publication_model.objects.count(), 3)
        self.assertEqual(self.evidence_model.objects.count(), 1)
