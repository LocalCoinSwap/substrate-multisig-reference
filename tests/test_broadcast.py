import unittest
from ksmref import utils

from substrateinterface import SubstrateInterface
import settings

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
    '''
