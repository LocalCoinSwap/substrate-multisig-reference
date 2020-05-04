import sys
import unittest


class TestLocalSanity(unittest.TestCase):
    def test_py_version(self):
        self.assertTrue(sys.version_info >= (3, 8))
