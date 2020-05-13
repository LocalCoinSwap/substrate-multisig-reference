import unittest

from scalecodec.base import ScaleDecoder
from scalecodec.block import ExtrinsicsDecoder
from substrateinterface import SubstrateInterface
from substrateinterface.utils.hasher import blake2_256
from substrateinterface.utils.ss58 import ss58_decode
from substrateinterface.utils.ss58 import ss58_encode

import settings
from bindings import sr25519

substrate = SubstrateInterface(
    url=settings.NODE_URL, address_type=2, type_registry_preset="kusama"
)
escrow_address = settings.escrow_address
trade_value = settings.trade_value
seller_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.seller_hexseed))
buyer_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.buyer_hexseed))
admin_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.admin_hexseed))


class TestSimpleSend(unittest.TestCase):
    def test_simple_send(self):
        # Key derivations for test
        sending_priv = seller_keypair[1].hex()
        sending_address = ss58_encode(seller_keypair[0], 2)
        sending_pub = ss58_decode(sending_address)

        substrate.init_runtime(block_hash=None)

        call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        call.encode(
            {
                "call_module": "Balances",
                "call_function": "transfer",
                "call_args": {"dest": escrow_address, "value": trade_value},
            }
        )

        response = substrate.get_runtime_state("System", "Account", [sending_address])
        assert response.get("result")
        nonce = response["result"].get("nonce", 0)
        genesis_hash = substrate.get_block_hash(0)

        era = "00"

        # Create signature payload
        signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")

        signature_payload.encode(
            {
                "call": str(call.data),
                "era": era,
                "nonce": nonce,
                "tip": 0,
                "specVersion": substrate.runtime_version,
                "genesisHash": genesis_hash,
                "blockHash": genesis_hash,
            }
        )

        # Sign payload
        data = str(signature_payload.data)
        if data[0:2] == "0x":
            data = bytes.fromhex(data[2:])
        else:
            data = data.encode()

        signature = sr25519.sign(
            (bytes.fromhex(sending_pub), bytes.fromhex(sending_priv)), data
        )

        signature = "0x{}".format(signature.hex())

        # Create extrinsic
        extrinsic = ScaleDecoder.get_decoder_class(
            "Extrinsic", metadata=substrate.metadata_decoder
        )

        extrinsic.encode(
            {
                "account_id": "0x" + sending_pub,
                "signature_version": 1,
                "signature": signature,
                "call_function": call.value["call_function"],
                "call_module": call.value["call_module"],
                "call_args": call.value["call_args"],
                "nonce": nonce,
                "era": "00",
                "tip": 0,
            }
        )

        self.assertEqual(len(str(extrinsic.data)), 288)

        """
        # This is how we would broadcast
        response = substrate.rpc_request(
            "author_submitExtrinsic", [str(extrinsic.data)]
        )
        extrinsic_hash = response["result"]
        print("Extrinsic sent: {}".format(extrinsic_hash))
        """


class TestMultiSigTrade(unittest.TestCase):
    def test_approve_as_multi(self):
        buyer_address = ss58_encode(buyer_keypair[0], 2)
        sending_address = ss58_encode(seller_keypair[0], 2)
        admin_address = ss58_encode(admin_keypair[0], 2)
        sending_priv = seller_keypair[1].hex()
        sending_pub = ss58_decode(sending_address)

        substrate.init_runtime(block_hash=None)

        inner_call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        inner_call.encode(
            {
                "call_module": "Balances",
                "call_function": "transfer",
                "call_args": {"dest": buyer_address, "value": trade_value},
            }
        )

        def hash_call(call):
            call = bytes.fromhex(str(call.data)[2:])
            return f"0x{blake2_256(call)}"

        hashed_call = hash_call(inner_call)
        expected_hash = (
            "0xf526cf0bfe78fcc5c2d69a44c7b10ca9533cadb95ed94fdcb1da14b50f3a27b0"
        )

        self.assertEqual(hashed_call, expected_hash)

        outer_call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        outer_call.encode(
            {
                "call_module": "Utility",
                "call_function": "approve_as_multi",
                "call_args": {
                    "call_hash": hashed_call,
                    "maybe_timepoint": None,
                    "other_signatories": [admin_address, buyer_address],
                    "threshold": 2,
                },
            }
        )

        response = substrate.get_runtime_state("System", "Account", [sending_address])
        assert response.get("result")
        nonce = response["result"].get("nonce", 0)
        genesis_hash = substrate.get_block_hash(0)

        era = "00"

        # Create signature payload
        signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")

        signature_payload.encode(
            {
                "call": str(outer_call.data),
                "era": era,
                "nonce": nonce,
                "tip": 0,
                "specVersion": substrate.runtime_version,
                "genesisHash": genesis_hash,
                "blockHash": genesis_hash,
            }
        )

        # Sign payload
        data = str(signature_payload.data)
        if data[0:2] == "0x":
            data = bytes.fromhex(data[2:])
        else:
            data = data.encode()

        signature = sr25519.sign(
            (bytes.fromhex(sending_pub), bytes.fromhex(sending_priv)), data
        )

        signature = "0x{}".format(signature.hex())

        # Create extrinsic
        extrinsic = ScaleDecoder.get_decoder_class(
            "Extrinsic", metadata=substrate.metadata_decoder
        )

        extrinsic.encode(
            {
                "account_id": "0x" + sending_pub,
                "signature_version": 1,
                "signature": signature,
                "call_function": outer_call.value["call_function"],
                "call_module": outer_call.value["call_module"],
                "call_args": outer_call.value["call_args"],
                "nonce": nonce,
                "era": "00",
                "tip": 0,
            }
        )

        """
        # This is how we would broadcast
        response = substrate.rpc_request(
            "author_submitExtrinsic", [str(extrinsic.data)]
        )
        print(response)
        extrinsic_hash = response["result"]
        print("Extrinsic sent: {}".format(extrinsic_hash))
        """
