# Generated by Django 5.2.1 on 2025-06-10 22:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "firebase_uid",
                    models.CharField(
                        blank=True,
                        help_text="The user ID from Firebase.",
                        max_length=128,
                        null=True,
                        unique=True,
                    ),
                ),
                (
                    "firebase_email_verified",
                    models.BooleanField(
                        default=False,
                        help_text="Whether the email address has been verified by Firebase.",
                    ),
                ),
                (
                    "firebase_photo_url",
                    models.URLField(
                        blank=True,
                        default="",
                        help_text="The URL of the user's profile picture from Firebase.",
                        max_length=500,
                    ),
                ),
                (
                    "firebase_display_name",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="The user's display name from Firebase.",
                        max_length=255,
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "User Profile",
                "verbose_name_plural": "User Profiles",
                "db_table": "core_user_profile",
            },
        ),
    ]
