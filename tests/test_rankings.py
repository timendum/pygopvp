import unittest

import pygopvp.rankings as rankings
from pygopvp.utils import LEAGUES


class TestRankings(unittest.TestCase):
    def test_load(self):
        self.assertGreater(len(list(rankings._load(LEAGUES[0].cp))), 300)
        self.assertGreater(len(list(rankings._load(LEAGUES[1].cp))), 200)
        self.assertGreater(len(list(rankings._load(LEAGUES[2].cp))), 100)
        self.assertGreater(len(list(rankings._load(LEAGUES[0].cp, "leads"))), 100)

    def test_generate(self):
        self.assertGreater(len(list(rankings.generate_from_rankings(LEAGUES[0].cp, top=20))), 9)
        self.assertGreater(len(list(rankings.generate_from_rankings(LEAGUES[1].cp, top=20))), 9)
        self.assertGreater(len(list(rankings.generate_from_rankings(LEAGUES[2].cp, top=20))), 9)
