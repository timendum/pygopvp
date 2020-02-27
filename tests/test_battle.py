import unittest

from pygopvp.model import Pokemon, Move
from pygopvp.battle import Battle


class TestBattle(unittest.TestCase):
    def test_battle_a(self):
        """Simpler: Only fast move, same timing, no effective type"""
        # https://pvpoke.com/battle/1500/arcanine/maractus/11/1-6-0/1-2-0/
        pokemona = Pokemon("ARCANINE", 19, [4, 8, 4], [Move("FIRE_FANG_FAST"), Move("WILD_CHARGE")])
        pokemonb = Pokemon(
            "MARACTUS", 24.5, [3, 14, 11], [Move("POISON_JAB_FAST"), Move("PETAL_BLIZZARD")],
        )
        battle = Battle([pokemona, pokemonb])
        battle.resolve()
        self.assertEqual(battle.pokemons[0].hp, 68)
        self.assertTrue(battle.pokemons[1].hp <= 0)
        self.assertEqual(battle.rate(0), 778)
        self.assertEqual(battle.rate(1), 221)
        self.assertEqual(battle.seconds, 10)

    def test_battle_b(self):
        """Effective type + charged"""
        # https://pvpoke.com/battle/1500/arcanine/poliwhirl/11/1-6-0/1-1-0/
        pokemona = Pokemon("ARCANINE", 19, [4, 8, 4], [Move("FIRE_FANG_FAST"), Move("WILD_CHARGE")])
        pokemonb = Pokemon(
            "POLIWHIRL", 40, [15, 15, 15], [Move("MUD_SHOT_FAST"), Move("BUBBLE_BEAM")]
        )
        battle = Battle([pokemona, pokemonb])
        battle.resolve()
        self.assertTrue(battle.pokemons[0].hp <= 0)
        self.assertEqual(battle.seconds, 55)

    def test_battle_c(self):
        """Different fast move timing"""
        # https://pvpoke.com/battle/1500/arcanine/maractus/11/1-6-0/0-2-0/
        pokemona = Pokemon("ARCANINE", 19, [4, 8, 4], [Move("FIRE_FANG_FAST"), Move("WILD_CHARGE")])
        pokemonb = Pokemon(
            "MARACTUS", 24.5, [3, 14, 11], [Move("BULLET_SEED_FAST"), Move("PETAL_BLIZZARD")],
        )
        battle = Battle([pokemona, pokemonb])
        battle.resolve()
        self.assertTrue(battle.pokemons[1].hp <= 0)
        self.assertEqual(battle.pokemons[0].hp, 98)
        self.assertEqual(battle.seconds, 10)
