import unittest

from scalecodec.base import ScaleDecoder
from substrateinterface import SubstrateInterface
from substrateinterface.utils.ss58 import ss58_decode
from substrateinterface.utils.ss58 import ss58_encode

import settings
from bindings import sr25519

substrate = SubstrateInterface(
    url=settings.NODE_URL, address_type=2, type_registry_preset="kusama"
)


class TestReferanceTransaction(unittest.TestCase):
    def test_referance_transaction(self):
        escrow_address = "HmGLJ6sG34vyBwyQSJWvN8HUByatcisuoyuyDXS4JeUZScm"

        tradeValue = 10000000000

        # Key derivations for test
        keypair = sr25519.pair_from_seed(bytes.fromhex(settings.sending_hexseed))
        sending_priv = keypair[1].hex()
        sending_address = ss58_encode(keypair[0], 2)
        sending_pub = ss58_decode(sending_address)

        substrate.init_runtime(block_hash=None)

        call = ScaleDecoder.get_decoder_class(
            "Call", metadata=substrate.metadata_decoder
        )

        call.encode(
            {
                "call_module": "Balances",
                "call_function": "transfer",
                "call_args": {"dest": escrow_address, "value": tradeValue},
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

        print("extrinsic", extrinsic)
        response = substrate.rpc_request(
            "author_submitExtrinsic", [str(extrinsic.data)]
        )
        extrinsic_hash = response["result"]
        print("Extrinsic sent: {}".format(extrinsic_hash))
