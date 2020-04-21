import os
import tempfile
import unittest

import pygopvp.customreader as customreader
from pygopvp.utils import LEAGUES

_TXT_CSV = """metagross,BULLET_PUNCH,METEOR_MASH,EARTHQUAKE
dragonite,DRAGON_BREATH,DRAGON_CLAW,OUTRAGE
kyogre,WATERFALL,SURF,BLIZZARD,35,1,2,3
mewtwo,PSYCHO_CUT,PSYSTRIKE,none"""


class TestCustomReader(unittest.TestCase):
    def setUp(self):
        self.temdir = tempfile.TemporaryDirectory()
        self.origin_DATA_DIR = customreader.DATA_DIR
        customreader.DATA_DIR = self.temdir.name
        with open(
            os.path.join(self.temdir.name, "custom-10000.txt"), "wt", encoding="utf-8"
        ) as ftxt:
            ftxt.write(_TXT_CSV)

    def tearDown(self):
        self.temdir.cleanup()
        customreader.DATA_DIR = self.origin_DATA_DIR

    def test_read_export(self):
        pokemons = list(customreader.generate_from_custom(LEAGUES[2].cp))
        self.assertEqual(len(pokemons), 4)
        self.assertEqual(pokemons[0].name, "METAGROSS")
        self.assertEqual(pokemons[0].level, 40)
        self.assertEqual(pokemons[0].attackIV, 15)
        self.assertEqual(pokemons[0].defenseIV, 15)
        self.assertEqual(pokemons[0].staminaIV, 15)
        self.assertEqual(pokemons[0].fast.moveId, "BULLET_PUNCH_FAST")
        self.assertEqual(pokemons[0].charged[0].moveId, "METEOR_MASH")
        self.assertEqual(pokemons[0].charged[1].moveId, "EARTHQUAKE")
        self.assertEqual(pokemons[2].level, 35)
        self.assertEqual(pokemons[2].attackIV, 1)
        self.assertEqual(pokemons[2].defenseIV, 2)
        self.assertEqual(pokemons[2].staminaIV, 3)
        self.assertEqual(len(pokemons[3].charged), 1)
