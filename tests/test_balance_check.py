import unittest

from scalecodec import ScaleBytes
from scalecodec.base import ScaleDecoder
from scalecodec.metadata import MetadataDecoder
from substrateinterface import SubstrateInterface
from substrateinterface.utils import hasher
from substrateinterface.utils import ss58

import settings
from ksmref import utils


class TestBalanceCheck(unittest.TestCase):
    def print_key_value(key, value):
        print()

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

    def test_balance_check_rpc_breakdown(self):
        """
        This test breaks down every RPC call that happens to get balance
        It is here only for the purpose of understanding how everything works

        Steps:

        Step 1: Initial preparatory steps
         - Connect to node
         - RPC Call 1: chain_getFinalisedHead
           - Get current finalised block hash

        Step 2: Get MetaData for the current block hash
         - RPC Call 2: state_getMetadata
         - Decode the result using MetadataDecoder and ScaleBytes

        Step 3: Prepare hashed data to make the next RPC call
         - We need three params hashed into one single hash string
           - Storage Module, Storage Function and Payload
         - Each param is encoded and hashed using various hashers
           Hasher for Payload is obtained from the dict at the bottom of the docstring

        Step 4: Get data at the storage hash prepared in Step 3
         - RPC Call 3: state_getStorageAt
         - Decode the data using ScaleDecoder's special class

        This is a key information used to encode/hash/decode in the entire function
        {
            'name': 'Account',
            'modifier': 'Default',
            'type': {
                'MapType': {
                    'hasher': 'Blake2_128Concat',
                    'key': 'AccountId',
                    'value': 'AccountInfo<Index, AccountData>',
                    'isLinked': False
                }
            },
        }
        """
        # Test data
        test_address = "HsgNgA5sgjuKxGUeaZPJE8rRn9RuixjvnPkVLFUYLEpj15G"

        ### STEP 1
        # Connect to the node
        substrate = SubstrateInterface(
            url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
        )

        # Get finalised block hash
        block_hash = substrate.rpc_request("chain_getFinalisedHead", []).get("result")
        if not block_hash:
            raise Exception("ERROR: RPC call for chain_getFinalisedHead failed")

        print("\n\n")
        print("-" * 100)
        print(f"BLOCK HASH: {block_hash}")

        ### STEP 2
        # Get metadata decoder, this is needed later
        metadata_result = substrate.rpc_request("state_getMetadata", [block_hash]).get(
            "result"
        )
        if not metadata_result:
            raise Exception("ERROR: RPC call for state_getMetadata failed")

        metadata_encoded = MetadataDecoder(ScaleBytes(metadata_result))
        metadata = metadata_encoded.decode()

        ### STEP 3
        # This comes from the metadata dict in the docstring `type` -> `MapType` -> `key`
        map_type_key = "AccountId"
        test_address_modified = "0x{}".format(ss58.ss58_decode(test_address, 2))
        print(f"TEST ADDRESS SS58 DECODED: {test_address_modified}")
        scale_decoder = ScaleDecoder.get_decoder_class(map_type_key)
        test_address_encoded = scale_decoder.encode(test_address_modified)
        print(f"TEST ADDRESS ENCODED: {test_address_encoded}")

        # Why blake2_128_concat? Because metadata dict in the docstring `type` -> `MapType` -> `hasher`
        test_address_hash = hasher.blake2_128_concat(test_address_encoded.data)

        # `System` is our module and `Account` if our function for this example
        storage_module = "System"
        storage_function = "Account"
        storage_module_hash = hasher.xxh128(storage_module.encode())
        storage_function_hash = hasher.xxh128(storage_function.encode())

        print(f"STORAGE MODULE: {storage_module}")
        print(f"STORAGE MODULE ENCODED: {storage_module.encode()}")
        print(f"STORAGE MODULE ENCODED HASHED: {storage_module_hash}")

        print(f"STORAGE FUNCTION: {storage_function}")
        print(f"STORAGE FUNCTION ENCODED: {storage_function.encode()}")
        print(f"STORAGE FUNCTION ENCODED HASHED: {storage_function_hash}")

        print(f"TEST ADDRESS: {test_address}")
        print(f"TEST ADDRESS SS58 DECODED: {test_address_modified}")
        print(f"TEST ADDRESS ENCODED: {test_address_encoded}")
        print(f"TEST ADDRESS ENCODED HASHED: {test_address_hash}")

        storage_hash = (
            f"0x"
            f"{storage_module_hash}"
            f"{storage_function_hash}"
            f"{test_address_hash}"
        )

        print(f"COMBINED HASH: {storage_hash}")

        ### STEP 4
        response = substrate.rpc_request(
            "state_getStorageAt", [storage_hash, block_hash]
        )
        result = response.get("result")
        if not result:
            raise Exception("ERROR: RPC call for state_getStorageAt failed")

        print(f"RPC RESULT: {result}")
        print("-" * 100)
        print("DECODING ABOVE RESULT ... ...")

        # This is again extracted from the metadata dict in the docstring `type` -> `MapType` -> `value`
        return_type = "AccountInfo<Index, AccountData>"
        result_decoded = ScaleDecoder.get_decoder_class(
            return_type, ScaleBytes(result), metadata=metadata
        ).decode()

        print(f"RESULT DECODED: {result_decoded}")
