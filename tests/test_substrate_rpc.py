import unittest

from scalecodec import ScaleBytes
from scalecodec.metadata import MetadataDecoder
from substrateinterface import SubstrateInterface

import settings


class TestExampleSubstrateRpc(unittest.TestCase):
    """
    Examples of some of RPC calls to substrate
    """

    def setUp(self):
        self.substrate = SubstrateInterface(
            url=settings.NODE_URL, address_type=2, type_registry_preset="kusama",
        )
        self.block_hash = self.substrate.rpc_request("chain_getFinalisedHead", [])[
            "result"
        ]
        print(self.block_hash)

    def test_get_block(self):
        data = self.substrate.rpc_request("chain_getBlock", [self.block_hash])["result"]
        print(data)
        # Next step would be to decode this response
        # But instead of writing this ourselves again, let's use
        # from py substrate library

    def test_get_block_hash_from_block_id(self):
        # Gets the genesis block
        block_id = 0
        data = self.substrate.rpc_request("chain_getBlockHash", [block_id])["result"]
        print(data)

    def test_get_block_metadata(self):
        data = self.substrate.rpc_request("state_getMetadata", [self.block_hash])[
            "result"
        ]

        metadata_decoder = MetadataDecoder(ScaleBytes(data))
        metadata = metadata_decoder.decode()

        print(metadata)
