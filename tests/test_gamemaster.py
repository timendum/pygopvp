from numbers import Real
import unittest

from pygopvp.gamemaster import POKEMONS, BUFFS, EFFECTIVE, MOVES, SETTINGS
from pygopvp.model import Type


class TestGameMaster(unittest.TestCase):
    def test_pokemons(self):
        self.assertTrue(len(POKEMONS) > 1251)
        self.assertIn("SMEARGLE", POKEMONS)
        self.assertTrue(len(POKEMONS["SMEARGLE"]["quickMoves"]) > 10)
        self.assertTrue(len(POKEMONS["SMEARGLE"]["cinematicMoves"]) > 10)

    def test_buffs(self):
        self.assertIn("minimumStatStage", BUFFS)
        self.assertIn("maximumStatStage", BUFFS)
        self.assertIsInstance(BUFFS["minimumStatStage"], int)
        self.assertIsInstance(BUFFS["maximumStatStage"], int)
        self.assertEqual(BUFFS["maximumStatStage"], -BUFFS["minimumStatStage"])
        self.assertIn("attackBuffMultiplier", BUFFS)
        self.assertEqual(len(BUFFS["attackBuffMultiplier"]), BUFFS["maximumStatStage"] * 2 + 1)
        self.assertIn("defenseBuffMultiplier", BUFFS)
        self.assertEqual(len(BUFFS["defenseBuffMultiplier"]), -BUFFS["minimumStatStage"] * 2 + 1)

    def test_effective(self):
        self.assertEqual(len(EFFECTIVE), 18)
        self.assertEqual(len(EFFECTIVE), len(Type))
        for elist in EFFECTIVE.values():
            self.assertEqual(len(elist), 18)
            for value in elist.values():
                self.assertIsInstance(value, Real)

    def test_moves(self):
        self.assertTrue(len(MOVES) > 200)
        for k, v in MOVES.items():
            self.assertIsInstance(k, str)
            self.assertIsInstance(v, dict)
            self.assertIn("uniqueId", v)

    def test_settings(self):
        self.assertTrue(len(SETTINGS) > 10)
        self.assertIn("maxEnergy", SETTINGS)
        self.assertIsInstance(SETTINGS["maxEnergy"], Real)
        self.assertIn("turnDurationSeconds", SETTINGS)
        self.assertIsInstance(SETTINGS["turnDurationSeconds"], Real)
        self.assertIn("chargeAttackBonusMultiplier", SETTINGS)
        self.assertIsInstance(SETTINGS["chargeAttackBonusMultiplier"], Real)
        self.assertIn("fastAttackBonusMultiplier", SETTINGS)
        self.assertIsInstance(SETTINGS["fastAttackBonusMultiplier"], Real)
        self.assertIn("sameTypeAttackBonusMultiplier", SETTINGS)
        self.assertIsInstance(SETTINGS["sameTypeAttackBonusMultiplier"], Real)
