import unittest

from ksmref import utils


class TestBalanceCheck(unittest.TestCase):
    def test_balance_check(self):
        # Note: If this test fails check funds has not be move from this address
        test_address = "HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G"

        exptected_result = {
            "free": 22000000000,
            "reserved": 0,
            "miscFrozen": 0,
            "feeFrozen": 0,
        }
        result = utils.get_balance_for_address(test_address)

        self.assertEqual(result, exptected_result)
