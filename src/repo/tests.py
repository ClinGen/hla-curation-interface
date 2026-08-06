import json
from typing import override

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from allele.models import Allele
from auth_.models import UserProfile
from common.tests import ProtectedViewTestMixin
from curation.constants.models.common import Status
from curation.constants.models.curation import CurationTypes
from curation.models import Curation
from disease.models import Disease
from repo.models import PublishedCuration


class PublishedCurationModelTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = User.objects.create_user(username="testuser", password="testpass")  # noqa: S106
        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.PROVISIONAL,
        )

    def test_create_published_curation(self):
        published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )
        self.assertEqual(published.curation, self.curation)
        self.assertEqual(published.published_by, self.user)
        self.assertEqual(published.version, 1)
        self.assertIsNotNone(published.published_at)

    def test_string_representation(self):
        self.curation.save()  # Ensure slug is generated.
        published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )
        self.assertEqual(str(published), f"Published: {self.curation.slug}")

    def test_one_to_one_constraint(self):
        PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )
        with self.assertRaises(IntegrityError):
            PublishedCuration.objects.create(
                curation=self.curation,
                published_by=self.user,
            )

    def test_reverse_relationship(self):
        published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )
        self.assertEqual(self.curation.publication, published)  # type: ignore

    def test_get_absolute_url(self):
        self.curation.save()  # Ensure slug is generated.
        published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )
        expected_url = reverse(
            "repo-detail", kwargs={"curation_slug": self.curation.slug}
        )
        self.assertEqual(published.get_absolute_url(), expected_url)


class CurationPublishViewTest(ProtectedViewTestMixin, TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]
    # Publish is a redirect action, not a page view, so these don't apply.
    template = ""
    page_name = ""
    expected_text: list[str] = []

    def setUp(self):
        self.url = ""  # Set a placeholder; will be updated after super().setUp()
        super().setUp()
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.PROVISIONAL,
        )
        self.curation.save()  # Ensure slug is generated.
        self.url = reverse(
            "curation-publish", kwargs={"curation_slug": self.curation.slug}
        )

    # Publish is a redirect action, not a page view, so skip inherited page tests.
    def test_template(self):
        pass

    def test_page_name_in_response(self):
        pass

    def test_expected_text_in_response(self):
        pass

    @override
    def test_permission_granted_if_yes_phi_yes_perms(self):
        # Publish always redirects (302) rather than returning 200, so we override.
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    def test_publish_provisional_curation(self):
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 1)
        self.curation.refresh_from_db()
        self.assertEqual(self.curation.status, Status.PUBLISHED)

    def test_cannot_publish_in_progress_curation(self):
        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.IN_PROGRESS,
        )
        curation.save()  # Ensure slug is generated.
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 0)

    def test_cannot_publish_already_published_curation(self):
        self.curation.status = Status.PUBLISHED
        self.curation.save()
        PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user4_yes_phi_yes_perms,
        )
        self.client.force_login(self.user4_yes_phi_yes_perms)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 1)


class RepoSearchViewTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        self.url = reverse("repo-search")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_displays_published_curations(self):
        allele = Allele.objects.get(pk=1)
        disease = Disease.objects.get(pk=1)
        user = User.objects.create_user(username="testuser", password="testpass")  # noqa: S106

        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=allele,
            disease=disease,
            status=Status.PUBLISHED,
        )
        curation.save()
        PublishedCuration.objects.create(
            curation=curation,
            published_by=user,
        )

        response = self.client.get(self.url)
        self.assertContains(response, curation.slug)


class PublishedCurationDetailViewTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        allele = Allele.objects.get(pk=1)
        disease = Disease.objects.get(pk=1)
        user = User.objects.create_user(username="testuser", password="testpass")  # noqa: S106

        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=allele,
            disease=disease,
            status=Status.PUBLISHED,
        )
        self.curation.save()
        self.published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=user,
        )

    def test_response_code(self):
        url = reverse("repo-detail", kwargs={"curation_slug": self.curation.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_displays_curation_details(self):
        url = reverse("repo-detail", kwargs={"curation_slug": self.curation.slug})
        response = self.client.get(url)
        self.assertContains(response, self.curation.slug)
        self.assertContains(response, "Download as JSON")


class JSONDownloadViewTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        allele = Allele.objects.get(pk=1)
        disease = Disease.objects.get(pk=1)
        user = User.objects.create_user(username="testuser", password="testpass")  # noqa: S106

        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=allele,
            disease=disease,
            status=Status.PUBLISHED,
        )
        self.curation.save()
        self.published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=user,
        )

    def test_download_single_json(self):
        url = reverse(
            "repo-download-single", kwargs={"curation_slug": self.curation.slug}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment", response["Content-Disposition"])

        data = json.loads(response.content)
        self.assertEqual(data["curation"]["curation_id"], self.curation.slug)

    def test_download_all_json(self):
        url = reverse("repo-download-all")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment", response["Content-Disposition"])

        data = json.loads(response.content)
        self.assertEqual(data["total_count"], 1)
        self.assertEqual(len(data["published_curations"]), 1)
        self.assertEqual(
            data["published_curations"][0]["curation_id"], self.curation.slug
        )


class ReadOnlyEnforcementTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        allele = Allele.objects.get(pk=1)
        disease = Disease.objects.get(pk=1)
        self.user = User.objects.create_user(username="testuser", password="testpass")  # noqa: S106
        UserProfile.objects.create(
            user=self.user,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
        )
        self.client.force_login(self.user)

        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=allele,
            disease=disease,
            status=Status.PUBLISHED,
        )
        self.curation.save()
        self.published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )

    def test_cannot_edit_published_evidence(self):
        url = reverse(
            "curation-edit-evidence", kwargs={"curation_slug": self.curation.slug}
        )
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("curation-detail", kwargs={"curation_slug": self.curation.slug}),
        )


class SupersessionTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = User.objects.create_user(username="superuser_t", password="pw")  # noqa: S106
        UserProfile.objects.create(
            user=self.user,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
        )

    def _make_published(self, forked_from: Curation | None = None) -> PublishedCuration:
        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.PUBLISHED,
            forked_from=forked_from,
        )
        return PublishedCuration.objects.create(
            curation=curation, published_by=self.user
        )

    def test_is_superseded_false_when_no_fork(self):
        from repo.views import is_superseded

        published = self._make_published()
        self.assertFalse(is_superseded(published))

    def test_is_superseded_true_when_fork_is_published(self):
        from repo.views import is_superseded

        original = self._make_published()
        self._make_published(forked_from=original.curation)
        self.assertTrue(is_superseded(original))

    def test_is_superseded_true_for_multi_hop_chain(self):
        from repo.views import is_superseded

        original = self._make_published()
        fork1 = self._make_published(forked_from=original.curation)
        self._make_published(forked_from=fork1.curation)
        self.assertTrue(is_superseded(original))

    def test_get_superseding_returns_none_when_not_superseded(self):
        from repo.views import get_superseding

        published = self._make_published()
        self.assertIsNone(get_superseding(published))

    def test_get_superseding_returns_fork(self):
        from repo.views import get_superseding

        original = self._make_published()
        fork_pub = self._make_published(forked_from=original.curation)
        result = get_superseding(original)
        self.assertEqual(result, fork_pub)


class ForkButtonTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = User.objects.create_user(username="fork_button_user", password="pw")  # noqa: S106
        UserProfile.objects.create(
            user=self.user,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
        )
        self.curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.PUBLISHED,
        )
        self.curation.save()
        self.published = PublishedCuration.objects.create(
            curation=self.curation, published_by=self.user
        )

    def test_fork_button_visible_for_curators(self):
        self.client.force_login(self.user)
        url = reverse("repo-detail", kwargs={"curation_slug": self.curation.slug})
        response = self.client.get(url)
        self.assertContains(response, "Fork")
