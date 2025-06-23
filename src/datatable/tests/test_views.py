"""Houses tests for the views module."""

from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse


class DatatableViewTest(TestCase):
    """Tests the datatable view."""

    fixtures = ["pokemon.json"]

    def setUp(self):
        """Sets up a Client for the tests."""
        self.user = User.objects.create(
            username="ash",
            password="pikachu",  # noqa: S106 (Hard-coded for testing.)
            email="ash@kantomail.net",
            is_staff=True,
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse("pokemon")

    def test_response_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_main_heading(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        main_heading = soup.find(id="main-heading").get_text().strip()
        self.assertEqual(main_heading, "Search Pokémon")

    def test_number_of_results_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        number_of_results = soup.find(id="number-of-results").get_text().strip()
        self.assertEqual(number_of_results, "800")

    def test_number_of_results_with_filter(self):
        response = self.client.get(self.url, {"generation": "1"})
        soup = BeautifulSoup(response.content, "html.parser")
        number_of_results = soup.find(id="number-of-results").get_text().strip()
        self.assertEqual(number_of_results, "166")

    def test_page_number_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        page_number = soup.find(id="page-1-button")
        self.assertIn("is-current", page_number["class"])

    def test_page_number_2(self):
        response = self.client.get(self.url, {"page": "2"})
        soup = BeautifulSoup(response.content, "html.parser")
        page_number = soup.find(id="page-2-button")
        self.assertIn("is-current", page_number["class"])

    def test_total_pages_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        page_number = soup.find(id="page-16-button").get_text().strip()
        self.assertEqual(page_number, "16")

    def test_pokedex_number_search_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        pokedex_number_search = soup.find(id="search-pokedex-number-input")
        self.assertNotEqual(pokedex_number_search["placeholder"], None)

    def test_pokedex_number_search_with_search(self):
        response = self.client.get(self.url, {"pokedex_number": "321"})
        soup = BeautifulSoup(response.content, "html.parser")
        pokedex_number_search = soup.find(id="search-pokedex-number-input")
        self.assertEqual(pokedex_number_search["value"], "321")

    def test_name_search_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        name_search = soup.find(id="search-name-input")
        self.assertNotEqual(name_search["placeholder"], None)

    def test_name_search_with_search(self):
        response = self.client.get(self.url, {"name": "Pi"})
        soup = BeautifulSoup(response.content, "html.parser")
        name_search = soup.find(id="search-name-input")
        self.assertEqual(name_search["value"], "Pi")

    def test_type1_select_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        type1_select = soup.find(id="filter-type1-select")
        selected = type1_select.find("option", selected=True)
        self.assertEqual(selected, None)

    def test_type1_select_with_filter(self):
        response = self.client.get(self.url, {"type1": "Water"})
        soup = BeautifulSoup(response.content, "html.parser")
        type1_select = soup.find(id="filter-type1-select")
        selected = type1_select.find("option", selected=True)
        self.assertEqual(selected["value"], "Water")

    def test_type2_select_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        type2_select = soup.find(id="filter-type2-select")
        selected = type2_select.find("option", selected=True)
        self.assertEqual(selected, None)

    def test_type2_select_with_filter(self):
        response = self.client.get(self.url, {"type2": "Electric"})
        soup = BeautifulSoup(response.content, "html.parser")
        type2_select = soup.find(id="filter-type2-select")
        selected = type2_select.find("option", selected=True)
        self.assertEqual(selected["value"], "Electric")

    def test_total_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        total_sort_button = soup.find(id="sort-total-button").get_text().strip()
        self.assertEqual(total_sort_button, "Sort Ascending")

    def test_total_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"total": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        total_sort_button = soup.find(id="sort-total-button").get_text().strip()
        self.assertEqual(total_sort_button, "Sort Descending")

    def test_total_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"total": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        total_sort_button = soup.find(id="sort-total-button").get_text().strip()
        self.assertEqual(total_sort_button, "Sort Default")

    def test_hp_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        hp_sort_button = soup.find(id="sort-hp-button").get_text().strip()
        self.assertEqual(hp_sort_button, "Sort Ascending")

    def test_hp_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"hp": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        hp_sort_button = soup.find(id="sort-hp-button").get_text().strip()
        self.assertEqual(hp_sort_button, "Sort Descending")

    def test_hp_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"hp": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        hp_sort_button = soup.find(id="sort-hp-button").get_text().strip()
        self.assertEqual(hp_sort_button, "Sort Default")

    def test_attack_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        attack_sort_button = soup.find(id="sort-attack-button").get_text().strip()
        self.assertEqual(attack_sort_button, "Sort Ascending")

    def test_attack_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"attack": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        attack_sort_button = soup.find(id="sort-attack-button").get_text().strip()
        self.assertEqual(attack_sort_button, "Sort Descending")

    def test_attack_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"attack": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        attack_sort_button = soup.find(id="sort-attack-button").get_text().strip()
        self.assertEqual(attack_sort_button, "Sort Default")

    def test_defense_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        defense_sort_button = soup.find(id="sort-defense-button").get_text().strip()
        self.assertEqual(defense_sort_button, "Sort Ascending")

    def test_defense_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"defense": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        defense_sort_button = soup.find(id="sort-defense-button").get_text().strip()
        self.assertEqual(defense_sort_button, "Sort Descending")

    def test_defense_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"defense": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        defense_sort_button = soup.find(id="sort-defense-button").get_text().strip()
        self.assertEqual(defense_sort_button, "Sort Default")

    def test_sp_atk_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        sp_atk_sort_button = soup.find(id="sort-sp-atk-button").get_text().strip()
        self.assertEqual(sp_atk_sort_button, "Sort Ascending")

    def test_sp_atk_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"sp_atk": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        sp_atk_sort_button = soup.find(id="sort-sp-atk-button").get_text().strip()
        self.assertEqual(sp_atk_sort_button, "Sort Descending")

    def test_sp_atk_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"sp_atk": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        sp_atk_sort_button = soup.find(id="sort-sp-atk-button").get_text().strip()
        self.assertEqual(sp_atk_sort_button, "Sort Default")

    def test_sp_def_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        sp_def_sort_button = soup.find(id="sort-sp-def-button").get_text().strip()
        self.assertEqual(sp_def_sort_button, "Sort Ascending")

    def test_sp_def_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"sp_def": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        sp_def_sort_button = soup.find(id="sort-sp-def-button").get_text().strip()
        self.assertEqual(sp_def_sort_button, "Sort Descending")

    def test_sp_def_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"sp_def": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        sp_def_sort_button = soup.find(id="sort-sp-def-button").get_text().strip()
        self.assertEqual(sp_def_sort_button, "Sort Default")

    def test_speed_sort_button_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        speed_sort_button = soup.find(id="sort-speed-button").get_text().strip()
        self.assertEqual(speed_sort_button, "Sort Ascending")

    def test_speed_sort_button_with_ascending_clicked(self):
        response = self.client.get(self.url, {"speed": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        speed_sort_button = soup.find(id="sort-speed-button").get_text().strip()
        self.assertEqual(speed_sort_button, "Sort Descending")

    def test_speed_sort_button_with_descending_clicked(self):
        response = self.client.get(self.url, {"speed": "desc"})
        soup = BeautifulSoup(response.content, "html.parser")
        speed_sort_button = soup.find(id="sort-speed-button").get_text().strip()
        self.assertEqual(speed_sort_button, "Sort Default")

    def test_generation_select_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        generation_select = soup.find(id="filter-generation-select")
        selected = generation_select.find("option", selected=True)
        self.assertEqual(selected, None)

    def test_generation_select_with_filter(self):
        response = self.client.get(self.url, {"generation": "5"})
        soup = BeautifulSoup(response.content, "html.parser")
        generation_select = soup.find(id="filter-generation-select")
        selected = generation_select.find("option", selected=True)
        self.assertEqual(selected["value"], "5")

    def test_legendary_select_default(self):
        response = self.client.get(self.url)
        soup = BeautifulSoup(response.content, "html.parser")
        legendary_select = soup.find(id="filter-legendary-select")
        selected = legendary_select.find("option", selected=True)
        self.assertEqual(selected, None)

    def test_legendary_select_with_filter(self):
        response = self.client.get(self.url, {"legendary": "True"})
        soup = BeautifulSoup(response.content, "html.parser")
        legendary_select = soup.find(id="filter-legendary-select")
        selected = legendary_select.find("option", selected=True)
        self.assertEqual(selected["value"], "True")

    def test_pokedex_number_search_results(self):
        response = self.client.get(self.url, {"pokedex_number": "1"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            pokedex_number = row.find_all("td")[0].get_text().strip()
            self.assertIn("1", pokedex_number)

    def test_name_search_results(self):
        response = self.client.get(self.url, {"name": "q"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            name = row.find_all("td")[1].get_text().strip().lower()
            self.assertIn("q", name)

    def test_type1_filter_results(self):
        response = self.client.get(self.url, {"type1": "Fairy"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            type1 = row.find_all("td")[2].get_text().strip()
            self.assertEqual(type1, "Fairy")

    def test_type2_filter_results(self):
        response = self.client.get(self.url, {"type2": "Steel"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            type2 = row.find_all("td")[3].get_text().strip()
            self.assertEqual(type2, "Steel")

    def test_total_sort_results(self):
        response = self.client.get(self.url, {"total": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_total = float("-inf")
        for row in rows:
            total = float(row.find_all("td")[4].get_text().strip())
            self.assertGreaterEqual(total, min_total)
            min_total = total

    def test_hp_sort_results(self):
        response = self.client.get(self.url, {"hp": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_hp = float("-inf")
        for row in rows:
            hp = float(row.find_all("td")[5].get_text().strip())
            self.assertGreaterEqual(hp, min_hp)
            min_hp = hp

    def test_attack_sort_results(self):
        response = self.client.get(self.url, {"attack": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_attack = float("-inf")
        for row in rows:
            attack = float(row.find_all("td")[6].get_text().strip())
            self.assertGreaterEqual(attack, min_attack)
            min_attack = attack

    def test_defense_sort_results(self):
        response = self.client.get(self.url, {"defense": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_defense = float("-inf")
        for row in rows:
            defense = float(row.find_all("td")[7].get_text().strip())
            self.assertGreaterEqual(defense, min_defense)
            min_defense = defense

    def test_sp_atk_sort_results(self):
        response = self.client.get(self.url, {"sp_atk": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_sp_atk = float("-inf")
        for row in rows:
            sp_atk = float(row.find_all("td")[8].get_text().strip())
            self.assertGreaterEqual(sp_atk, min_sp_atk)
            min_sp_atk = sp_atk

    def test_sp_def_sort_results(self):
        response = self.client.get(self.url, {"sp_def": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_sp_def = float("-inf")
        for row in rows:
            sp_def = float(row.find_all("td")[9].get_text().strip())
            self.assertGreaterEqual(sp_def, min_sp_def)
            min_sp_def = sp_def

    def test_speed_sort_results(self):
        response = self.client.get(self.url, {"speed": "asc"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        min_speed = float("-inf")
        for row in rows:
            speed = float(row.find_all("td")[10].get_text().strip())
            self.assertGreaterEqual(speed, min_speed)
            min_speed = speed

    def test_generation_filter_results(self):
        response = self.client.get(self.url, {"generation": "3"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            generation = row.find_all("td")[11].get_text().strip()
            self.assertEqual(generation, "3")

    def test_legendary_filter_results(self):
        response = self.client.get(self.url, {"legendary": "True"})
        soup = BeautifulSoup(response.content, "html.parser")
        rows = soup.find("tbody").find_all("tr")
        for row in rows:
            legendary = row.find_all("td")[12].get_text().strip()
            self.assertEqual(legendary, "True")
