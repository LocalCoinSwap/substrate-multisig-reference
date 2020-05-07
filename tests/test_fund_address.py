import unittest

from substrateinterface import SubstrateInterface


class TestFundAddress(unittest.TestCase):
    # Recreate tx 0x12a01d2c50714a25e15e2eac9376693aa3fdb8a80260b609cbdb08b8a0aef47c 
    def test_unsigned(self):
        substrate = SubstrateInterface(
            url="wss://kusama-rpc.polkadot.io/",
            address_type=2,
            type_registry_preset="kusama",
        )

        # Blockchain info we need, there are already python methods to decode these if required
        block = substrate.get_chain_block()['block']
        block_number = block['header']['number']
        block_hash = substrate.get_block_hash(block_number)
        genesis_hash = substrate.get_block_hash(0)
        metadata_rpc = substrate.get_block_metadata(block_hash)
        spec_version = substrate.rpc_request('state_getRuntimeVersion', [block_hash])['result']['specVersion']
        registry = substrate.get_type_registry(block_hash)
        sender_address =
        sender_nonce = 
                # Confirm with js versions that this function still works
                # Also called args or method in tx-wraper
        method_w_args = substrate.compose_call(
        call_module='Balances',
        call_function='transfer',
        call_params={
            'dest': 'HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G',
            'value': 22000000000,
        }
        )

        #self.assertTrue(free_balance == 22000000000,)

    def test_sign(self):
        # I think this is the data signed
        signed = 'f0448a4b380489ef1e07ede22a4112cc2a3a1229152cfb1904e88cec7b2ca2250e82901bf15bca6bf26d67756013472af3b8072706e3f7a7a30936c0068d498f'
        #signAndSend


