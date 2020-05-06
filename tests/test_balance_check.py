import unittest

from substrateinterface import SubstrateInterface


class TestBalanceCheck(unittest.TestCase):
    def test_balance_check(self):
        # Note: If this test fails check funds has not be move from this address
        test_address = "HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G"

        substrate = SubstrateInterface(
            url="wss://kusama-rpc.polkadot.io/",
            address_type=2,
            type_registry_preset="kusama",
        )
        block = substrate.get_chain_finalised_head()

        account_data = substrate.get_runtime_state(
            module="System",
            storage_function="Account",
            params=[test_address],
            block_hash=block,
        )
        print(account_data["result"]["data"]["free"])
        free_balance = account_data["result"]["data"]["free"]
        self.assertEqual(free_balance, 22000000000)
