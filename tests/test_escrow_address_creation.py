import binascii
import unittest

from substrateinterface.utils.ss58 import ss58_decode
from substrateinterface.utils.ss58 import ss58_encode

from bindings import multisig


class TestEscrowAddressCreation(unittest.TestCase):
    def test_create_escrow_address(self):
        buyer_addr = "CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo"
        seller_addr = "J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc"
        admin_addr = "HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2"

        def kusama_addr_to_account_id(address):
            decoded_addr = ss58_decode(address)
            decoded_addr_bytes = bytes.fromhex(decoded_addr)
            return decoded_addr_bytes

        buyer_id = kusama_addr_to_account_id(buyer_addr)
        seller_id = kusama_addr_to_account_id(seller_addr)
        admin_id = kusama_addr_to_account_id(admin_addr)

        trade_addresses = sorted([buyer_id, seller_id, admin_id])

        escrow_addr = multisig.multi_account_id(trade_addresses, 2)

        escrow_addr = binascii.hexlify(bytearray(escrow_addr)).decode("ascii")
        print(ss58_encode(escrow_addr, 2))
