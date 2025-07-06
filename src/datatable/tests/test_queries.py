"""Houses tests for the queries module."""

from django.test import RequestFactory, TestCase

from datatable import queries
from datatable.models import Pokemon


class QueriesTest(TestCase):
    """Tests the queries module."""

    fixtures = ["test_pokemon.json"]

    def setUp(self):
        """Sets up a RequestFactory and sets up our Pokémon QuerySet."""
        self.factory = RequestFactory()
        self.pokemon = Pokemon.objects.all()

    def test_search_pokedex_number(self):
        request = self.factory.get("/", {"pokedex_number": "623"})
        queryset = queries.search(request, self.pokemon, "pokedex_number")
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().name, "Golurk")

    def test_search_name(self):
        request = self.factory.get("/", {"name": "Bulbasaur"})
        queryset = queries.search(request, self.pokemon, "name")
        self.assertEqual(queryset.count(), 1)
        self.assertEqual(queryset.first().name, "Bulbasaur")

    def test_filter_type1(self):
        request = self.factory.get("/", {"type1": "Grass"})
        queryset = queries.filter_(request, self.pokemon, "type1")
        self.assertGreater(queryset.count(), 0)
        self.assertEqual(queryset.count(), 70)

    def test_filter_type2(self):
        request = self.factory.get("/", {"type2": "Ice"})
        queryset = queries.filter_(request, self.pokemon, "type2")
        self.assertGreater(queryset.count(), 0)
        self.assertEqual(queryset.count(), 14)

    def test_sort_total_asc(self):
        request = self.factory.get("/", {"total": "asc"})
        queryset = queries.sort(request, self.pokemon, "total")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Sunkern", "Azurill", "Kricketot"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_hp_asc(self):
        request = self.factory.get("/", {"hp": "asc"})
        queryset = queries.sort(request, self.pokemon, "hp")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Shedinja", "Diglett", "Magikarp"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_attack_asc(self):
        request = self.factory.get("/", {"attack": "asc"})
        queryset = queries.sort(request, self.pokemon, "attack")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Chansey", "Happiny", "Magikarp"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_defense_asc(self):
        request = self.factory.get("/", {"defense": "asc"})
        queryset = queries.sort(request, self.pokemon, "defense")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Chansey", "Happiny", "Blissey"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_sp_atk_asc(self):
        request = self.factory.get("/", {"sp_atk": "asc"})
        queryset = queries.sort(request, self.pokemon, "sp_atk")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Shuckle", "Feebas", "Bonsly"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_sp_def_asc(self):
        request = self.factory.get("/", {"sp_def": "asc"})
        queryset = queries.sort(request, self.pokemon, "sp_def")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Caterpie", "Weedle", "Magikarp"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_speed_asc(self):
        request = self.factory.get("/", {"speed": "asc"})
        queryset = queries.sort(request, self.pokemon, "speed")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Shuckle", "Munchlax", "Trapinch"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_total_desc(self):
        request = self.factory.get("/", {"total": "desc"})
        queryset = queries.sort(request, self.pokemon, "total")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = [
            "MewtwoMega Mewtwo X",
            "MewtwoMega Mewtwo Y",
            "RayquazaMega Rayquaza",
        ]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_hp_desc(self):
        request = self.factory.get("/", {"hp": "desc"})
        queryset = queries.sort(request, self.pokemon, "hp")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Blissey", "Chansey", "Wobbuffet"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_attack_desc(self):
        request = self.factory.get("/", {"attack": "desc"})
        queryset = queries.sort(request, self.pokemon, "attack")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = [
            "MewtwoMega Mewtwo X",
            "HeracrossMega Heracross",
            "GroudonPrimal Groudon",
        ]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_defense_desc(self):
        request = self.factory.get("/", {"defense": "desc"})
        queryset = queries.sort(request, self.pokemon, "defense")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = [
            "SteelixMega Steelix",
            "Shuckle",
            "AggronMega Aggron",
        ]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_sp_atk_desc(self):
        request = self.factory.get("/", {"sp_atk": "desc"})
        queryset = queries.sort(request, self.pokemon, "sp_atk")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = [
            "MewtwoMega Mewtwo Y",
            "KyogrePrimal Kyogre",
            "RayquazaMega Rayquaza",
        ]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_sp_def_desc(self):
        request = self.factory.get("/", {"sp_def": "desc"})
        queryset = queries.sort(request, self.pokemon, "sp_def")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Shuckle", "Regice", "KyogrePrimal Kyogre"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_total_none(self):
        request = self.factory.get("/", {"total": "none"})
        queryset = queries.sort(request, self.pokemon, "total")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_hp_none(self):
        request = self.factory.get("/", {"hp": "none"})
        queryset = queries.sort(request, self.pokemon, "hp")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_attack_none(self):
        request = self.factory.get("/", {"attack": "none"})
        queryset = queries.sort(request, self.pokemon, "attack")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_defense_none(self):
        request = self.factory.get("/", {"defense": "none"})
        queryset = queries.sort(request, self.pokemon, "defense")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_sp_atk_none(self):
        request = self.factory.get("/", {"sp_atk": "none"})
        queryset = queries.sort(request, self.pokemon, "sp_atk")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_sp_def_none(self):
        request = self.factory.get("/", {"sp_def": "none"})
        queryset = queries.sort(request, self.pokemon, "sp_def")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_speed_none(self):
        request = self.factory.get("/", {"speed": "none"})
        queryset = queries.sort(request, self.pokemon, "speed")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = ["Bulbasaur", "Ivysaur", "Venusaur"]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_sort_speed_desc(self):
        request = self.factory.get("/", {"speed": "desc"})
        queryset = queries.sort(request, self.pokemon, "speed")
        all_names = list(queryset.values_list("name", flat=True))
        self.assertGreater(len(all_names), 3)
        actual_first_three_names = all_names[:3]
        expected_first_three_names = [
            "Deoxysspeed Forme",
            "Ninjask",
            "AlakazamMega Alakazam",
        ]
        self.assertEqual(actual_first_three_names, expected_first_three_names)

    def test_filter_generation(self):
        request = self.factory.get("/", {"generation": "1"})
        queryset = queries.filter_(request, self.pokemon, "generation")
        generation_list = list(queryset.values_list("generation", flat=True))
        self.assertEqual(len(generation_list), 166)
        only_1s = True
        for num in generation_list:
            if num != 1:
                only_1s = False
        self.assertTrue(only_1s)

    def test_filter_legendary(self):
        request = self.factory.get("/", {"legendary": "True"})
        queryset = queries.filter_(request, self.pokemon, "legendary")
        legendary_list = list(queryset.values_list("legendary", flat=True))
        self.assertEqual(len(legendary_list), 65)
        only_legendaries = True
        for val in legendary_list:
            if val is False:
                only_legendaries = False
        self.assertTrue(only_legendaries)
