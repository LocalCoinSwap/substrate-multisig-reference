import unittest

from ksmref import utils


class TestBroadcast(unittest.TestCase):
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
    def test_get_tx_info(self):
        """Test that we can get exctrinsic info from hash"""
        tx_hash = '0x5d66ccff882e61ce8845cc462d553c87b9007c91dfd817b3a63f578f510368ed'

        def get_tx_info(tx_hash):
            substrate = SubstrateInterface(
            url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
            )

        #self.assertEqual(result[1], True)

    def test_class(self):
    extrinsic = '0x2d0284dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b01feb2a3c3f562e8e59d3c8c5323023289fdd95ddd277c9b992ce4f6ed0151c6504bc26cb0e71f9adc05adde23a941b3b0c2ae0a1f1befa21f878639dbd9b98b840040000400f68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa3302286bee'
    rpc = utils.rpcInterface(
    url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
    )
    x = rpc.rpc_request(method="author_submitAndWatchExtrinsic", params=[extrinsic])
    print(x)
    self.assertEqual(x, True)
    '''
