from math import floor
import unittest

from pygopvp.model import BasePokemon, Pokemon, Move
from pygopvp.utils import Type
from pygopvp.gamemaster import POKEMONS


class TestBasePokemon(unittest.TestCase):
    def test_generate_all(self):
        pokemons = [BasePokemon(name) for name in POKEMONS]
        reprs = [repr(pokemon) for pokemon in pokemons]
        self.assertTrue(len(reprs) > 1)

    def test_fail(self):
        try:
            BasePokemon("NotAPokemon Name")
        except Exception as e:
            self.assertIsInstance(e, KeyError)
            return
        self.fail("No exception")

    def test_title(self):
        self.assertEqual(BasePokemon("MUK").title(), "Muk")
        self.assertEqual(BasePokemon("MUK_ALOLA").title(), "Muk (Alolan)")


class TestPokemon(unittest.TestCase):
    def test_properties(self):
        bulbasaur = Pokemon("BULBASAUR", 15, [15, 13, 14])
        self.assertEqual(floor(bulbasaur.attack), 68)
        self.assertEqual(floor(bulbasaur.defense), 64)
        self.assertEqual(bulbasaur.startHp, 73)
        self.assertEqual(bulbasaur.cp, 472)
        rayquaza = Pokemon("RAYQUAZA", 24, [4, 7, 15])
        self.assertEqual(floor(rayquaza.attack), 188)
        self.assertEqual(floor(rayquaza.defense), 115)
        self.assertEqual(rayquaza.startHp, 149)
        self.assertEqual(rayquaza.cp, 2477)
        # half level
        maractus = Pokemon("MARACTUS", 24.5, [3, 14, 11], [None, None])
        self.assertEqual(maractus.startHp, 126)
        self.assertEqual(maractus.cp, 1483)

    def test_rapr(self):
        pokemon = Pokemon("PRIMEAPE", 15, [0, 2, 4], [Move("LOW_KICK_FAST"), Move("CLOSE_COMBAT")])
        self.assertEqual(
            repr(pokemon),
            "Pokemon('PRIMEAPE', 15, [0, 2, 4], [Move('LOW_KICK_FAST'), Move('CLOSE_COMBAT')])",
        )
        pokemon = Pokemon(
            "GROWLITHE",
            15,
            [0, 2, 4],
            [Move("EMBER_FAST"), Move("FLAME_WHEEL"), Move("FLAMETHROWER")],
        )
        self.assertEqual(
            repr(pokemon),
            "Pokemon('GROWLITHE', 15, [0, 2, 4], [Move('EMBER_FAST'), Move('FLAME_WHEEL'), Move('FLAMETHROWER')])",
        )

    def test_find_max(self):
        arcanine = Pokemon.find_max("ARCANINE", 1500)
        self.assertEqual(arcanine.cp, 1498)
        self.assertEqual(arcanine.level, 18.5)
        self.assertEqual(arcanine.attackIV, 0)
        self.assertEqual(arcanine.defenseIV, 14)
        self.assertEqual(arcanine.staminaIV, 15)
        slowbro = Pokemon("SLOWBRO", 40, [12, 14, 15], [None, None])
        self.assertEqual(slowbro.cp, 2498)
        self.assertEqual(slowbro.level, 40)
        self.assertEqual(slowbro.attackIV, 12)
        self.assertEqual(slowbro.defenseIV, 14)
        self.assertEqual(slowbro.staminaIV, 15)

    def test_find_by_cp(self):
        arcanine = Pokemon.find_by_cp("ARCANINE", 1498)
        self.assertEqual(arcanine.cp, 1498)
        mewtwo = Pokemon.find_by_cp("MEWTWO", 3531)
        self.assertEqual(mewtwo.cp, 3531)
        impossible = Pokemon.find_by_cp("MEWTWO", 20)
        self.assertIsNone(impossible)


class TestMove(unittest.TestCase):
    def test_properties(self):
        move = Move("FURY_CUTTER_FAST")
        self.assertTrue(move.is_fast)
        self.assertFalse(move.is_charged)
        move = Move("DARK_PULSE")
        self.assertFalse(move.is_fast)
        self.assertTrue(move.is_charged)
        move = Move("TRANSFORM_FAST")  # corner case, energyDelta = 0
        self.assertTrue(move.is_fast)
        self.assertFalse(move.is_charged)

    def test_rapr(self):
        move = Move("COUNTER_FAST")
        self.assertEqual(repr(move), "Move('COUNTER_FAST')")

    def test_best_dpt_moves(self):
        bests = Move.best_dpt_moves(
            ["STEEL_WING_FAST", "AIR_SLASH_FAST"], ["BRAVE_BIRD", "SKY_ATTACK", "FLASH_CANNON"]
        )
        self.assertEqual(len(bests), 3)
        self.assertEqual(bests[0], "AIR_SLASH_FAST")
        self.assertEqual(bests[1], "BRAVE_BIRD")
        self.assertEqual(bests[2], "SKY_ATTACK")
        # simple
        bests = Move.best_dpt_moves(["LOCK_ON_FAST"], ["FLASH_CANNON", "BODY_SLAM"])
        self.assertEqual(len(bests), 3)
        self.assertEqual(bests[0], "LOCK_ON_FAST")
        self.assertEqual(bests[1], "BODY_SLAM")
        self.assertEqual(bests[2], "FLASH_CANNON")
        # with STAB bonus
        bests = Move.best_dpt_moves(["LOCK_ON_FAST"], ["FLASH_CANNON", "BODY_SLAM"], [Type.STEEL])
        self.assertEqual(len(bests), 3)
        self.assertEqual(bests[0], "LOCK_ON_FAST")
        self.assertEqual(bests[1], "FLASH_CANNON")
        self.assertEqual(bests[2], "BODY_SLAM")
        bests = Move.best_dpt_moves(
            ["BITE_FAST", "POISON_JAB_FAST", "SNARL_FAST"],
            ["DARK_PULSE", "GUNK_SHOT", "SLUDGE_WAVE", "ACID_SPRAY"],
        )
        self.assertEqual(len(bests), 3)
        self.assertEqual(bests[0], "SNARL_FAST")
        self.assertEqual(bests[1], "GUNK_SHOT")
        self.assertEqual(bests[2], "SLUDGE_WAVE")
