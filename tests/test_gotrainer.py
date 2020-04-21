import unittest

from pygopvp.gotrainer import genate_from_leader
from pygopvp.utils import LEAGUES


class TestGameMasterMiners(unittest.TestCase):
    def test_read_export_ok(self):
        for league in LEAGUES:
            for trainer in ("CANDELA", "BLANCHE", "SPARK"):
                pokemons = genate_from_leader(trainer, league)
                self.assertEqual(len(pokemons), 3)

    def test_ko(self):
        try:
            genate_from_leader("NONE", LEAGUES[0])
        except Exception as e:
            self.assertIsInstance(e, ValueError)
