"""Houses tests for the curation app's data migrations."""

from django.apps.registry import Apps
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from django.test import TransactionTestCase

from allele.models import Allele
from curation.constants.models.curation import CurationTypes
from curation.models import Curation
from disease.models import Disease

BEFORE = [("curation", "0020_alter_curation_copied_from_and_more")]
AFTER = [("curation", "0021_rename_status_codes")]


class RenameStatusCodesTest(TransactionTestCase):
    """Checks that 0021 maps RFR/PRO to PRV/APR, and back."""

    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        allele = Allele.objects.get(pk=1)
        disease = Disease.objects.get(pk=1)
        self.pks = [
            Curation.objects.create(
                curation_type=CurationTypes.ALLELE, allele=allele, disease=disease
            ).pk
            for _ in range(3)
        ]

    def tearDown(self):
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(executor.loader.graph.leaf_nodes())

    def _migrate(self, targets: list[tuple[str, str]]) -> Apps:
        executor = MigrationExecutor(connection)
        executor.loader.build_graph()
        executor.migrate(targets)
        return executor.loader.project_state(targets).apps

    def _set_statuses(self, apps: Apps, statuses: list[str]) -> None:
        for model_name in ("Curation", "HistoricalCuration"):
            model = apps.get_model("curation", model_name)
            for pk, status in zip(self.pks, statuses, strict=True):
                pk_field = "id" if model_name == "HistoricalCuration" else "pk"
                model.objects.filter(**{pk_field: pk}).update(status=status)

    def _statuses(self, apps: Apps, model_name: str) -> list[set[str]]:
        model = apps.get_model("curation", model_name)
        pk_field = "id" if model_name == "HistoricalCuration" else "pk"
        return [
            set(model.objects.filter(**{pk_field: pk}).values_list("status", flat=True))
            for pk in self.pks
        ]

    def test_forward_maps_old_codes_to_new(self):
        apps = self._migrate(BEFORE)
        self._set_statuses(apps, ["RFR", "PRO", "INP"])
        apps = self._migrate(AFTER)
        for model_name in ("Curation", "HistoricalCuration"):
            self.assertEqual(
                self._statuses(apps, model_name), [{"PRV"}, {"APR"}, {"INP"}]
            )

    def test_backward_maps_new_codes_to_old(self):
        apps = self._migrate(AFTER)
        self._set_statuses(apps, ["PRV", "APR", "INP"])
        apps = self._migrate(BEFORE)
        for model_name in ("Curation", "HistoricalCuration"):
            self.assertEqual(
                self._statuses(apps, model_name), [{"RFR"}, {"PRO"}, {"INP"}]
            )
