import unittest

import xxhash
from substrateinterface import SubstrateInterface

import settings

substrate = SubstrateInterface(
    url=settings.NODE_URL, address_type=2, type_registry_preset="kusama"
)


class TestHistoricalEventQuery(unittest.TestCase):
    def test_historical_query(self):
        a = bytearray(xxhash.xxh64("System", seed=0).digest())
        b = bytearray(xxhash.xxh64("System", seed=1).digest())
        c = bytearray(xxhash.xxh64("Events", seed=0).digest())
        d = bytearray(xxhash.xxh64("Events", seed=1).digest())
        a.reverse()
        b.reverse()
        c.reverse()
        d.reverse()
        storage_key = f"0x{a.hex()}{b.hex()}{c.hex()}{d.hex()}"

        expected_key = (
            "0x26aa394eea5630e07c48ae0c9558cef780d41e5e16056765bc8461851072c9d7"
        )

        self.assertEqual(storage_key, expected_key)

        test_block = (
            "0x9371a6742726810f20ef7e26c53a141270d76e50b2c636baa4a0a1f5961f33ef"
        )
        result = substrate.rpc_request("state_getStorage", [storage_key, test_block])[
            "result"
        ]

        expected_result = (
            "0x1800000000000000c0257a09000000000200000001000000000000ca9a3b000000000200000"
            "0020000001102da91521070ef71375c5db41bc7f6276b3048178bd7456322fbced4a756886620"
            "e58625bc778dcd2dd0faaba532be4cdc0a44a5796eacbd6297c8783698d526d8f526cf0bfe78f"
            "cc5c2d69a44c7b10ca9533cadb95ed94fdcb1da14b50f3a27b00000020000000d060008af2f00"
            "000000000000000000000000000200000002041a7938fede32e1275281b3eee5708706d88444a"
            "6dc898a4dec463f1eb298463f00c2eb0b000000000000000000000000000002000000000000a8"
            "250a00000000000000"
        )

        self.assertEqual(result, expected_result)
        print("result", result)

        # Do it with py-substrate
        event_info = substrate.get_runtime_state(
            module="System", storage_function="Events", block_hash=test_block
        ).get("result")

        expected_event_info = [
            {
                "phase": 0,
                "extrinsic_idx": 0,
                "type": "0000",
                "module_id": "System",
                "event_id": "ExtrinsicSuccess",
                "params": [
                    {
                        "type": "DispatchInfo",
                        "value": {
                            "weight": 159000000,
                            "class": "Mandatory",
                            "paysFee": False,
                        },
                        "valueRaw": "",
                    }
                ],
                "topics": [],
                "event_idx": 0,
            },
            {
                "phase": 0,
                "extrinsic_idx": 1,
                "type": "0000",
                "module_id": "System",
                "event_id": "ExtrinsicSuccess",
                "params": [
                    {
                        "type": "DispatchInfo",
                        "value": {
                            "weight": 1000000000,
                            "class": "Mandatory",
                            "paysFee": False,
                        },
                        "valueRaw": "",
                    }
                ],
                "topics": [],
                "event_idx": 1,
            },
            {
                "phase": 0,
                "extrinsic_idx": 2,
                "type": "1102",
                "module_id": "Utility",
                "event_id": "NewMultisig",
                "params": [
                    {
                        "type": "AccountId",
                        "value": "0xda91521070ef71375c5db41bc7f6276b3048178bd7456322fbced4a756886620",
                        "valueRaw": "da91521070ef71375c5db41bc7f6276b3048178bd7456322fbced4a756886620",
                    },
                    {
                        "type": "AccountId",
                        "value": "0xe58625bc778dcd2dd0faaba532be4cdc0a44a5796eacbd6297c8783698d526d8",
                        "valueRaw": "e58625bc778dcd2dd0faaba532be4cdc0a44a5796eacbd6297c8783698d526d8",
                    },
                    {
                        "type": "CallHash",
                        "value": "0xf526cf0bfe78fcc5c2d69a44c7b10ca9533cadb95ed94fdcb1da14b50f3a27b0",
                        "valueRaw": "f526cf0bfe78fcc5c2d69a44c7b10ca9533cadb95ed94fdcb1da14b50f3a27b0",
                    },
                ],
                "topics": [],
                "event_idx": 2,
            },
            {
                "phase": 0,
                "extrinsic_idx": 2,
                "type": "0d06",
                "module_id": "Treasury",
                "event_id": "Deposit",
                "params": [
                    {
                        "type": "Balance",
                        "value": 800000000,
                        "valueRaw": "0008af2f000000000000000000000000",
                    }
                ],
                "topics": [],
                "event_idx": 3,
            },
            {
                "phase": 0,
                "extrinsic_idx": 2,
                "type": "0204",
                "module_id": "Balances",
                "event_id": "Deposit",
                "params": [
                    {
                        "type": "AccountId",
                        "value": "0x1a7938fede32e1275281b3eee5708706d88444a6dc898a4dec463f1eb298463f",
                        "valueRaw": "1a7938fede32e1275281b3eee5708706d88444a6dc898a4dec463f1eb298463f",
                    },
                    {
                        "type": "Balance",
                        "value": 200000000,
                        "valueRaw": "00c2eb0b000000000000000000000000",
                    },
                ],
                "topics": [],
                "event_idx": 4,
            },
            {
                "phase": 0,
                "extrinsic_idx": 2,
                "type": "0000",
                "module_id": "System",
                "event_id": "ExtrinsicSuccess",
                "params": [
                    {
                        "type": "DispatchInfo",
                        "value": {
                            "weight": 170240000,
                            "class": "Normal",
                            "paysFee": False,
                        },
                        "valueRaw": "",
                    }
                ],
                "topics": [],
                "event_idx": 5,
            },
        ]

        self.assertEqual(event_info, expected_event_info)
