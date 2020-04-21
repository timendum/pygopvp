import unittest

from pygopvp.gotrainer import read_export
from pygopvp.utils import LEAGUES


class TestGameMasterMiners(unittest.TestCase):
    def test_read_export_ok(self):
        for league in LEAGUES:
            for trainer in ("CANDELA", "BLANCHE", "SPARK"):
                pokemons = read_export(trainer, league)
                self.assertEqual(len(pokemons), 3)

    def test_ko(self):
        try:
            read_export("NONE", LEAGUES[0])
        except Exception as e:
            self.assertIsInstance(e, ValueError)
