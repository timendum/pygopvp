import tempfile
import unittest
import os

import pygopvp.utils as utils


class TestUtils(unittest.TestCase):
    def setUp(self):
        utils.write_cache()  # preserve old cache
        self.temdir = tempfile.TemporaryDirectory()
        self.origin_DATA_DIR = utils.DATA_DIR
        utils.DATA_DIR = self.temdir.name
        utils.start_cache()

    def tearDown(self):
        self.temdir.cleanup()
        utils.DATA_DIR = self.origin_DATA_DIR

    def test_compatible_leagues(self):
        self.assertEqual(len(utils.compatible_leagues(10)), 3)
        self.assertEqual(len(utils.compatible_leagues(2000)), 2)
        self.assertEqual(len(utils.compatible_leagues(5000)), 1)
        self.assertIsInstance(utils.compatible_leagues(5000)[0][0], str)
        self.assertIsInstance(utils.compatible_leagues(5000)[0][1], int)
        leagues = utils.compatible_leagues(10)
        self.assertLess(leagues[0][1], leagues[1][1])
        self.assertLess(leagues[1][1], leagues[2][1])

    def test_cache(self):
        self._called = 0

        def sum(a: int, b: int):
            self._called += 1
            return a + b

        self.assertEqual(sum(1, 2), 3)
        self._called = 0
        self.assertEqual(utils.json_cache(sum, 1, 2), 3)
        self.assertEqual(self._called, 1)  # called
        self.assertEqual(utils.json_cache(sum, 1, 2), 3)
        self.assertEqual(self._called, 1)  # not called!
        utils.write_cache()
        # File written
        self.assertGreater(len(os.listdir(self.temdir.name)), 0)
