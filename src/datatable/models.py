"""Houses database models for testing the datatable app."""

from django.db import models


class Pokemon(models.Model):
    """Contains information about a Pokémon.

    This model is only used in testing.
    """

    pokedex_number: models.IntegerField = models.IntegerField(
        verbose_name="Pokédex Number"
    )
    name = models.CharField(verbose_name="Name")
    type1 = models.CharField(verbose_name="Type 1")
    type2 = models.CharField(verbose_name="Type 2")
    total = models.IntegerField(verbose_name="Total")
    hp = models.IntegerField(verbose_name="HP")
    attack = models.IntegerField(verbose_name="Attack")
    defense = models.IntegerField(verbose_name="Defense")
    sp_atk = models.IntegerField(verbose_name="Sp. Atk")
    sp_def = models.IntegerField(verbose_name="Sp. Def")
    speed = models.IntegerField(verbose_name="Speed")
    generation = models.IntegerField(verbose_name="Generation")
    legendary = models.BooleanField(verbose_name="Legendary")

    class Meta:
        """Defines metadata options."""

        db_table = "pokemon"
        verbose_name = "Pokémon"
        verbose_name_plural = "Pokémon"

    def __str__(self) -> str:
        """Returns a string representation of the Pokémon."""
        return self.name
