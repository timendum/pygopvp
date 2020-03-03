import unittest

from pygopvp.utils import compatible_leagues


class TestUtils(unittest.TestCase):
    def test_compatible_leagues(self):
        self.assertEqual(len(compatible_leagues(10)), 3)
        self.assertEqual(len(compatible_leagues(2000)), 2)
        self.assertEqual(len(compatible_leagues(5000)), 1)
        self.assertIsInstance(compatible_leagues(5000)[0][0], str)
        self.assertIsInstance(compatible_leagues(5000)[0][1], int)
        leagues = compatible_leagues(10)
        self.assertLess(leagues[0][1], leagues[1][1])
        self.assertLess(leagues[1][1], leagues[2][1])
