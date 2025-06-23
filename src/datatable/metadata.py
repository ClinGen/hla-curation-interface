"""Houses the metadata for the columns of the datatable."""

from datatable.constants import FieldTypes, Filters, SortDirections

TYPE_OPTIONS = [
    Filters.DEFAULT,
    "Bug",
    "Dark",
    "Dragon",
    "Electric",
    "Fairy",
    "Fighting",
    "Fire",
    "Flying",
    "Ghost",
    "Grass",
    "Ground",
    "Ice",
    "Normal",
    "Poison",
    "Psychic",
    "Rock",
    "Steel",
    "Water",
    Filters.NONE,
]

GENERATION_OPTIONS = [Filters.DEFAULT, "1", "2", "3", "4", "5", "6"]

LEGENDARY_OPTIONS = [Filters.DEFAULT, "True", "False"]

FIELDS = [
    {
        "text": "Number",
        "param_name": "pokedex_number",
        "id": "pokedex-number",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Name",
        "param_name": "name",
        "id": "name",
        "default_value": "",
        "type": FieldTypes.SEARCH,
        "placeholder": "",
    },
    {
        "text": "Type 1",
        "param_name": "type1",
        "id": "type1",
        "default_value": TYPE_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": TYPE_OPTIONS,
    },
    {
        "text": "Type 2",
        "param_name": "type2",
        "id": "type2",
        "default_value": TYPE_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": TYPE_OPTIONS,
    },
    {
        "text": "Total",
        "param_name": "total",
        "id": "total",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "HP",
        "param_name": "hp",
        "id": "hp",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "Attack",
        "param_name": "attack",
        "id": "attack",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "Defense",
        "param_name": "defense",
        "id": "defense",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "Sp. Atk",
        "param_name": "sp_atk",
        "id": "sp-atk",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "Sp. Def",
        "param_name": "sp_def",
        "id": "sp-def",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "Speed",
        "param_name": "speed",
        "id": "speed",
        "default_value": SortDirections.DEFAULT,
        "type": FieldTypes.SORT,
    },
    {
        "text": "Generation",
        "param_name": "generation",
        "id": "generation",
        "default_value": GENERATION_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": GENERATION_OPTIONS,
    },
    {
        "text": "Legendary",
        "param_name": "legendary",
        "id": "legendary",
        "default_value": LEGENDARY_OPTIONS[0],
        "type": FieldTypes.FILTER,
        "options": LEGENDARY_OPTIONS,
    },
]
