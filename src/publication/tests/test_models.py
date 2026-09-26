from django.core.exceptions import ValidationError
from django.test import TestCase

from publication.models import Publication


class PublicationTest(TestCase):
    def test_requires_pubmed_id(self):
        publication = Publication(title="Common diseases in Pokémon")
        with self.assertRaises(ValidationError) as context:
            publication.full_clean()
        self.assertIn("pubmed_id", context.exception.message_dict)

    def test_string_representation_uses_pubmed_id(self):
        publication = Publication(title="Common diseases in Pokémon.", pubmed_id="123")
        self.assertEqual(str(publication), "Common diseases in Pokémon (PMID:123).")
