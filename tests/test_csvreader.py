import os
import tempfile
import unittest

import pygopvp.csvreader as csvreader
from pygopvp.utils import LEAGUES

_TXT_CSV = """Ancestor?,Scan date,Nr,Name,Nickname,Gender,Level,possibleLevels,CP,HP,Dust cost,Overall appraisal,ATT max?,DEF max?,HP max?,Stats appraisal,min IV%,ØIV%,max IV%,ØATT IV,ØDEF IV,ØHP IV,Unique?,Fast move,Special move,Special move 2,DPS,Box,Custom1,Custom2,Saved,Form,Egg,Lucky,BuddyBoosted,ShadowForm
0,2/21/20 15:49:44,320,Wailmer,22+≈06,♀,22.0,22.0,752,175,3000,?,0,0,0,?,13.3,13.3,13.3,1.3,1.7,3.0,0,Splash,Water Pulse,- ,9.6,da evolvere,,,0,319,0,1,0,0
0,2/21/20 12:17:45,374,Beldum,20+≈39,,20.0,20.0,544,78,2500,?,0,0,0,?,84.4,86.7,88.9,14.5,13.0,11.5,0,Take Down,Struggle,- ,7.6,da evolvere,,,0,1226,0,1,0,1
0,2/19/20 12:02:23,471,Glaceon,28+41❄️❄️3❄️2,♂,28.0,28.0,2478,125,4500,?,0,0,0,?,91.1,91.1,91.1,15.0,11.0,15.0,1,Ice Shard,Icy Wind,Avalanche,29.6,Default,,,0,514,0,1,0,0
1,2/19/20 12:02:23,471,Glaceon,-,-,26.0,26.0,2301,121,4000,?,0,0,0,?,91.1,91.1,91.1,15.0,11.0,15.0,1,-,-,-,-,Default,,,0,514,0,1,0,0
0,2/20/20 15:01:49,9,Blastoise,15+≈41◐○1,♂,15.0,15.0,1044,104,1900,?,0,0,0,?,88.9,90.0,91.1,14.5,12.0,14.0,0,Bite,Skull Bash,- ,12.8,Default,,,0,605,0,1,0,1"""


class TestCustomReader(unittest.TestCase):
    def setUp(self):
        self.temdir = tempfile.TemporaryDirectory()
        self.origin_DATA_DIR = csvreader.DATA_DIR
        csvreader.DATA_DIR = self.temdir.name
        with open(
            os.path.join(self.temdir.name, "history_20991231_235959.csv"), "wt", encoding="utf-8"
        ) as ftxt:
            ftxt.write(_TXT_CSV)

    def tearDown(self):
        self.temdir.cleanup()
        csvreader.DATA_DIR = self.origin_DATA_DIR

    def test_read_export(self):
        pokemons = list(csvreader.read_export())
        self.assertEqual(len(pokemons), 4)
        self.assertEqual(pokemons[0].name, "WAILMER")
        self.assertEqual(pokemons[0].level, 22)
        self.assertEqual(pokemons[0].fast.moveId, "SPLASH_FAST")
        self.assertEqual(len(pokemons[0].charged), 1)
        self.assertEqual(pokemons[0].charged[0].moveId, "WATER_PULSE")
        self.assertEqual(pokemons[3].name, "BLASTOISE")
