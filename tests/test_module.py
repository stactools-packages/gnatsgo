import unittest

import stactools.gnatsgo


class TestModule(unittest.TestCase):
    def test_version(self):
        self.assertIsNotNone(stactools.gnatsgo.__version__)
