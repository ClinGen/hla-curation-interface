"""Houses tests for the repo app."""

import json

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import Client, TestCase
from django.urls import reverse

from allele.models import Allele
from core.models import UserProfile
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
            status=Status.DONE,
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
        self.assertEqual(self.curation.publication, published)

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


class CurationPublishViewTest(TestCase):
    fixtures = ["test_alleles.json", "test_diseases.json"]

    def setUp(self):
        self.client = Client()
        self.allele = Allele.objects.get(pk=1)
        self.disease = Disease.objects.get(pk=1)
        self.user = User.objects.create_user(username="testuser", password="testpass")  # noqa: S106
        UserProfile.objects.create(
            user=self.user,
            has_signed_phi_agreement=True,
            has_curation_permissions=True,
        )
        self.client.force_login(self.user)

    def test_publish_done_curation(self):
        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.DONE,
        )
        curation.save()  # Ensure slug is generated.
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(hasattr(curation, "publication"))
        self.assertEqual(PublishedCuration.objects.count(), 1)

    def test_cannot_publish_in_progress_curation(self):
        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.IN_PROGRESS,
        )
        curation.save()  # Ensure slug is generated.
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 0)

    def test_cannot_publish_already_published_curation(self):
        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.DONE,
        )
        curation.save()  # Ensure slug is generated.
        PublishedCuration.objects.create(
            curation=curation,
            published_by=self.user,
        )

        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 1)

    def test_requires_authentication(self):
        self.client.logout()
        curation = Curation.objects.create(
            curation_type=CurationTypes.ALLELE,
            allele=self.allele,
            disease=self.disease,
            status=Status.DONE,
        )
        curation.save()
        url = reverse("curation-publish", kwargs={"curation_slug": curation.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(PublishedCuration.objects.count(), 0)


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
            status=Status.DONE,
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
            status=Status.DONE,
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
        self.assertContains(response, "Published Curation Details")


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
            status=Status.DONE,
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
        self.assertEqual(data["curation_id"], self.curation.slug)

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
            status=Status.DONE,
        )
        self.curation.save()
        self.published = PublishedCuration.objects.create(
            curation=self.curation,
            published_by=self.user,
        )

    def test_cannot_edit_published_curation(self):
        url = reverse("curation-edit", kwargs={"curation_slug": self.curation.slug})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("curation-detail", kwargs={"curation_slug": self.curation.slug}),
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
