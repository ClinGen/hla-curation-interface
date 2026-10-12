"""Fills in the authors of publications that were added before authors were stored."""

import logging
import os
import time

from django.core.management.base import BaseCommand, CommandParser

from publication.clients import refresh_from_pubmed
from publication.models import Publication

logger = logging.getLogger(__name__)

# NCBI allows 10 requests a second with an API key and 3 without. Stay a bit under.
DELAY_WITH_API_KEY = 0.15
DELAY_WITHOUT_API_KEY = 0.4


class Command(BaseCommand):
    help = (
        "Refreshes every publication that has no authors from PubMed, which also "
        "updates its title, primary author, and year."
    )

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="List the publications that would be refreshed, without contacting "
            "PubMed or saving anything.",
        )

    def handle(self, *_args: object, **options: object) -> None:
        publications = list(Publication.objects.filter(authors="").order_by("pk"))
        if options["dry_run"]:
            for publication in publications:
                self.stdout.write(f"{publication.slug} (PMID:{publication.pubmed_id})")
            self.stdout.write(f"Would refresh {len(publications)} publications.")
            return

        delay = (
            DELAY_WITH_API_KEY if os.getenv("PUBMED_API_KEY") else DELAY_WITHOUT_API_KEY
        )
        updated = failed = 0
        for index, publication in enumerate(publications):
            if index:
                time.sleep(delay)
            if refresh_from_pubmed(publication):
                publication.save()
                updated += 1
            else:
                message = (
                    f"Unable to refresh {publication.slug} "
                    f"(PMID:{publication.pubmed_id}) from PubMed."
                )
                logger.warning(message)
                self.stderr.write(message)
                failed += 1
        self.stdout.write(f"Updated {updated} publications; failed {failed}.")
