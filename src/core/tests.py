"""Houses tests for the core app."""

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from core.crud import create_user_profile, read_user_profile, update_user_profile
from core.models import UserProfile


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("home")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "HLA Curation Interface")


class AboutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("about")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "About")
        self.assertContains(response, "HLA Curation Interface (HCI)")
        self.assertContains(response, "alleles")
        self.assertContains(response, "haplotypes")
        self.assertContains(response, "Stanford University")


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("contact")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Contact")
        self.assertContains(response, "email")
        self.assertContains(response, "helpdesk@clinicalgenome.org")


class HelpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("help")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Help")
        self.assertContains(response, "user documentation")
        self.assertContains(response, "email")
        self.assertContains(response, "helpdesk@clinicalgenome.org")


class CitingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("citing")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Citing")
        self.assertContains(response, "format")
        self.assertContains(response, "dataset")


class AcknowledgementsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("acknowledgements")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Acknowledgements")
        self.assertContains(response, "NIH/NHGRI")
        self.assertContains(response, "Steven Mack")


class CollaboratorsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("collaborators")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_content(self):
        response = self.client.get(self.url)
        self.assertContains(response, "Collaborators")
        self.assertContains(response, "The Baylor College of Medicine ClinGen Team")
        self.assertContains(response, "PharmGKB")


class CRUDTest(TestCase):
    def setUp(self):
        self.user_ash = User.objects.create(username="ash", password="pikachu")  # noqa: S106 (Hard-coded for testing.)
        self.user_oak = User.objects.create(username="oak", password="#1prof")  # noqa: S106 (Hard-coded for testing.)
        self.user_profile_oak = UserProfile.objects.create(
            user=self.user_oak,
            firebase_uid=self.user_oak.username,
            firebase_email_verified=False,
            firebase_photo_url="https://www.kantopeople.net/img/oak.jpg",
            firebase_display_name="Oak",
            firebase_sign_in_provider="password",
        )

    def test_create_non_existent_user(self):
        create = create_user_profile(
            username="misty",
            email_verified=True,
            photo_url="https://www.kantopeople.net/img/misty.jpg",
            display_name="Misty",
            provider="password",
        )
        self.assertIsNone(create)

    def test_create_existing_user(self):
        username = "ash"
        email_verified = True
        photo_url = "https://www.kantopeople.net/img/ash.jpg"
        display_name = "Ash"
        provider = "password"
        user_profile, user = create_user_profile(
            username=username,
            email_verified=email_verified,
            photo_url=photo_url,
            display_name=display_name,
            provider=provider,
        )
        self.assertEqual(self.user_ash.username, user.username)
        self.assertEqual(self.user_ash.email, user.email)
        self.assertEqual(username, user_profile.firebase_uid)
        self.assertEqual(email_verified, user_profile.firebase_email_verified)
        self.assertEqual(photo_url, user_profile.firebase_photo_url)
        self.assertEqual(display_name, user_profile.firebase_display_name)
        self.assertEqual(provider, user_profile.firebase_sign_in_provider)

    def test_read_non_existent_user(self):
        read = read_user_profile("brock")
        self.assertIsNone(read)

    def test_read_existing_user(self):
        user_profile, user = read_user_profile("oak")
        self.assertEqual(self.user_oak.username, user.username)
        self.assertEqual(self.user_oak.email, user.email)
        self.assertEqual(self.user_profile_oak.user, user)
        self.assertEqual(self.user_profile_oak.firebase_uid, user_profile.firebase_uid)
        self.assertEqual(
            self.user_profile_oak.firebase_email_verified,
            user_profile.firebase_email_verified,
        )
        self.assertEqual(
            self.user_profile_oak.firebase_photo_url, user_profile.firebase_photo_url
        )
        self.assertEqual(
            self.user_profile_oak.firebase_display_name,
            user_profile.firebase_display_name,
        )
        self.assertEqual(
            self.user_profile_oak.firebase_sign_in_provider,
            user_profile.firebase_sign_in_provider,
        )

    def test_update_non_existent_user(self):
        update = update_user_profile(
            username="misty",
            email_verified=True,
            photo_url="https://www.kantopeople.net/img/misty.jpg",
            display_name="Misty",
            provider="password",
        )
        self.assertIsNone(update)

    def test_update_existing_user(self):
        new_email_verified = True
        new_photo_url = "https://www.kantopeople.net/img/oak2.jpg"
        new_display_name = "Prof. Oak"
        new_provider = "google.com"
        user_profile, user = update_user_profile(
            username="oak",
            email_verified=new_email_verified,
            photo_url=new_photo_url,
            display_name=new_display_name,
            provider=new_provider,
        )
        self.assertEqual(self.user_oak.username, user.username)
        self.assertEqual(self.user_oak.email, user.email)
        self.assertEqual(new_email_verified, user_profile.firebase_email_verified)
        self.assertEqual(new_photo_url, user_profile.firebase_photo_url)
        self.assertEqual(new_display_name, user_profile.firebase_display_name)
        self.assertEqual(new_provider, user_profile.firebase_sign_in_provider)
