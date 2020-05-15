import unittest

from substrateinterface import SubstrateInterface

import settings
from ksmref import utils


substrate = SubstrateInterface(
    url=settings.NODE_URL, address_type=2, type_registry_preset="kusama"
)


class TestMultiSignatureTrade(unittest.TestCase):
    def test_simple_transfer_fee(self):
        signed_extrinsic = "0x2d0284dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b01b24406f04393e57af7d7f0dc0332c0a47af5a58e4d1ed7f85448d3f0dee135361b720f4da59152e94c447ca43afb4df676af89f1c8c3625fd29e33357099bf8f006c000400dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b02286bee"
        fee_info = utils.get_fee_info(signed_extrinsic)
        expected_fee_info = {
            "class": "normal",
            "partialFee": "1000000000",
            "weight": 195000000,
        }
        self.assertEqual(fee_info, expected_fee_info)

    def test_approve_as_multi_fee(self):
        signed_extrinsic = "0x2d03840c85dc20f15e3d8328b6a162d47ce43771fe6925f0effb8b878bcd1ff28d8f120118b0ba5b963ed1560b54479933b084b469e752ed87c95e7f8024ed89fc04062774d8a9b956bad6a7da07da5b5b556e6ec677dcbdd111864c715368b24568be87002000180302000818ada844614318a831c7bf07c42d0a1eee8a8f6fbbe9b96d0b6de7938eec21313c552ba63f8c373b52bd58731d84632ef41cc117297c8961fc5d71e4cc37c91300634e7881418164b4394d84e7d9d6ed9d68f574041106546d1bdcded79e00cdea"
        fee_info = utils.get_fee_info(signed_extrinsic)
        expected_fee_info = {
            "class": "normal",
            "partialFee": "1000000000",
            "weight": 170240000,
        }
        self.assertEqual(fee_info, expected_fee_info)

    """
    def test_as_multi_fee(self):
        signed_extrinsic = 'Todo'
        fee_info = utils.get_fee_info(signed_extrinsic)
        expected_fee_info = 'Todo'
        self.assertEqual(fee_info, expected_fee_info)
    """
