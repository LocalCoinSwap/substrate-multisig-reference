import unittest

import settings
from ksmref import utils


class TestBroadcast(unittest.TestCase):
    '''
    def test_broadcast(self):
        """Test that we can broadcast an exctrinsic
        # Note: Requires fresh signed extrinsic each time
        # Use https://polkadot.js.org/apps/#/accounts:
        # Click send, enter destination and amount, click next,
        # Click slider on bottom left 'Sign and Submit' to make sure it is off
        """
        extrinsic = ""

        result = utils.broadcast(extrinsic)
        print("result", result)
        self.assertEqual(result[1], True)
    '''

    def test_class(self):
        extrinsic = "0x2d0284dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b01ec704f7f86300f40345a2f071d1914ea861a248ca6b982c4c935dde380246070be75f16e571553e304ea9d1bad28b092930d8e96377dca7066e849aecebef78f0060000400f68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa3302286bee"
        rpc = utils.rpcInterface(
            url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
        )
        x = rpc.rpc_request(method="author_submitAndWatchExtrinsic", params=[extrinsic])
        print(x)
        self.assertEqual(x, True)

    '''
    def test_get_tx_info(self):
        """Test that we can get exctrinsic info from hash"""
        tx_hash = '0x5d66ccff882e61ce8845cc462d553c87b9007c91dfd817b3a63f578f510368ed'

        def get_tx_info(tx_hash):
            substrate = SubstrateInterface(
            url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
            )

        #self.assertEqual(result[1], True)


    '''
