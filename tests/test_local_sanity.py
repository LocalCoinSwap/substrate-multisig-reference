import sys
import unittest


class TestLocalSanity(unittest.TestCase):
    def test_py_version(self):
        print(sys.version_info)
        self.assertTrue(sys.version_info >= (3, 8))
