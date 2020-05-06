import binascii
import unittest

from substrateinterface.utils.ss58 import ss58_encode

from bindings import bip39
from bindings import sr25519


class TestMnemonicFromPolkadotJSDerivation(unittest.TestCase):
    def test_chrome_extension_mnemonic(self):
        mnemonic = (
            "prefer fashion insect dizzy energy marble"
            " forget artefact aspect short surface leave"
        )
        seed_array = bip39.bip39_to_mini_secret(mnemonic, "")
        seed = binascii.hexlify(bytearray(seed_array)).decode("ascii")

        seed_from_mnemonic = (
            "3f686928bda5b57a0992c999aea74d" "65f844be234686871a2ddc6b003d586786"
        )

        self.assertEqual(seed, seed_from_mnemonic)

        expected_publickey = (
            "8852f77f2aea5d2d5808cefa7cd49a3ed" "0ce1f1aa8ff2564c3cb96cb2510337d"
        )

        keypair = sr25519.pair_from_seed(bytes.fromhex(seed_from_mnemonic))
        public_key = keypair[0].hex()

        self.assertEqual(public_key, expected_publickey)

        expected_address = "Ff4gBd7WcHgsNVhr5HGPQXQx4PzPHGtHdNVaCRK5d5KeMHh"

        address = ss58_encode(keypair[0], 2)

        self.assertEqual(address, expected_address)


class TestTradeParticipentsMnemonics(unittest.TestCase):
    def test_trading_participent_mnemonics(self):
        buyer_mnemonic = (
            "boy impose motor jump pear car"
            " pet exact gravity section amazing marble"
            " exit trim two doctor depart rose"
            " guitar injury today stock fruit surface"
        )

        seller_mnemonic = (
            "virus custom dismiss own coconut wood"
            " infant profit august need industry false"
            " isolate arctic panic sure museum feature"
            " anchor spin tooth aunt mouse whisper"
        )

        admin_mnemonic = (
            "gain toe suspect good drop board"
            " uphold garment sponsor snap bachelor unusual"
            " bicycle snake leisure alarm voice record"
            " finger sense market hire sure sweet"
        )

        def mnemonic_to_seed(mnemonic):
            seed_array = bip39.bip39_to_mini_secret(mnemonic, "")
            return binascii.hexlify(bytearray(seed_array)).decode("ascii")

        def decompose_seed(seed):
            keypair = sr25519.pair_from_seed(bytes.fromhex(seed))
            public_key = keypair[0].hex()
            private_key = keypair[1].hex()
            address = ss58_encode(keypair[0], 2)
            return address, public_key, private_key

        def print_stats(stats):
            print(
                f"[ADDRESS] {stats[0]}"
                f"\n[PUBLIC KEY] {stats[1]}"
                f"\n[PRIVATE KEY] {stats[2]}\n"
            )

        buyer_details = decompose_seed(mnemonic_to_seed(buyer_mnemonic))
        seller_details = decompose_seed(mnemonic_to_seed(seller_mnemonic))
        admin_details = decompose_seed(mnemonic_to_seed(admin_mnemonic))

        self.assertEqual(
            buyer_details[0], "CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo"
        )
        self.assertEqual(
            seller_details[0], "J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc"
        )
        self.assertEqual(
            admin_details[0], "HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2"
        )

        print("\n\nBUYER")
        print_stats(buyer_details)
        print("SELLER")
        print_stats(seller_details)
        print("ADMIN")
        print_stats(admin_details)
