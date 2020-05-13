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
seller_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.seller_hexseed))
buyer_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.buyer_hexseed))
admin_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.admin_hexseed))


class TestMultiSignatureTrade(unittest.TestCase):
    """
    Demonstrate a 3 transaction typical trade.

    1. Seller places funds in escrow address (multisig)
    2. Seller authorises release to buyer after being paid in fiat
    3. Admin finalises release to buyer
    """

    def setUp(self):
        self.buyer_address = ss58_encode(buyer_keypair[0], 2)
        self.seller_address = ss58_encode(seller_keypair[0], 2)
        self.admin_address = ss58_encode(admin_keypair[0], 2)
        self.seller_priv = seller_keypair[1].hex()
        self.seller_pub = ss58_decode(self.seller_address)
        self.admin_priv = admin_keypair[1].hex()
        self.admin_pub = ss58_decode(self.admin_address)

        substrate.init_runtime(block_hash=None)

        # Prepare the inner call as we will reuse it, lets not write code twice
        self.inner_call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        self.inner_call.encode(
            {
                "call_module": "Balances",
                "call_function": "transfer",
                "call_args": {
                    "dest": self.buyer_address,
                    "value": settings.trade_value,
                },
            }
        )

        # Figure out how to set these automatically
        self.multi_tx_blocknum = 2290447
        self.multi_tx_index = 2

    def test_a_seller_fund_escrow(self):
        print("Seller places funds into escrow")

        call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        call.encode(
            {
                "call_module": "Balances",
                "call_function": "transfer",
                "call_args": {
                    "dest": settings.escrow_address,
                    "value": settings.trade_value,
                },
            }
        )

        response = substrate.get_runtime_state(
            "System", "Account", [self.seller_address]
        )
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
            (bytes.fromhex(self.seller_pub), bytes.fromhex(self.seller_priv)), data
        )

        signature = "0x{}".format(signature.hex())

        # Create extrinsic
        extrinsic = ScaleDecoder.get_decoder_class(
            "Extrinsic", metadata=substrate.metadata_decoder
        )

        extrinsic.encode(
            {
                "account_id": "0x" + self.seller_pub,
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

    def test_b_seller_approve_as_multi(self):
        print("Seller broadcasts approve as multi")

        # Function that hashes call with blake2_256
        def hash_call(call):
            call = bytes.fromhex(str(call.data)[2:])
            return f"0x{blake2_256(call)}"

        hashed_call = hash_call(self.inner_call)
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
                    "other_signatories": [self.admin_address, self.buyer_address],
                    "threshold": 2,
                },
            }
        )

        response = substrate.get_runtime_state(
            "System", "Account", [self.seller_address]
        )
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
            (bytes.fromhex(self.seller_pub), bytes.fromhex(self.seller_priv)), data
        )

        signature = "0x{}".format(signature.hex())

        # Create extrinsic
        extrinsic = ScaleDecoder.get_decoder_class(
            "Extrinsic", metadata=substrate.metadata_decoder
        )

        extrinsic.encode(
            {
                "account_id": "0x" + self.seller_pub,
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

    def test_c_admin_as_multi(self):
        print("Admin finalises release of funds")
        outer_call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        outer_call.encode(
            {
                "call_module": "Utility",
                "call_function": "as_multi",
                "call_args": {
                    "call": self.inner_call.serialize(),
                    "maybe_timepoint": {
                        "height": self.multi_tx_blocknum,
                        "index": self.multi_tx_index,
                    },
                    "other_signatories": [self.buyer_address, self.seller_address],
                    "threshold": 2,
                },
            }
        )

        response = substrate.get_runtime_state(
            "System", "Account", [self.admin_address]
        )
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
            (bytes.fromhex(self.admin_pub), bytes.fromhex(self.admin_priv)), data
        )

        signature = "0x{}".format(signature.hex())

        # Create extrinsic
        extrinsic = ScaleDecoder.get_decoder_class(
            "Extrinsic", metadata=substrate.metadata_decoder
        )

        extrinsic.encode(
            {
                "account_id": "0x" + self.admin_pub,
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
