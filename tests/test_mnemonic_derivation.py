import unittest

from substrateinterface.utils.ss58 import ss58_encode

from bindings import wasm_crypto


class TestMnemonicDerivation(unittest.TestCase):
    def test_chrome_extension_mnemonic(self):
        # mnemonic = """
        # prefer fashion insect dizzy energy marble forget
        # artefact aspect short surface leave
        # """
        seed_from_mnemonic = (
            "3f686928bda5b57a0992c999aea74d65f844be234686871a2ddc6b003d586786"
        )
        expected_publickey = (
            "8852f77f2aea5d2d5808cefa7cd49a3ed0ce1f1aa8ff2564c3cb96cb2510337d"
        )

        keypair = wasm_crypto.pair_from_seed(bytes.fromhex(seed_from_mnemonic))
        public_key = keypair[0].hex()

        self.assertTrue(public_key == expected_publickey)

        expected_address = "Ff4gBd7WcHgsNVhr5HGPQXQx4PzPHGtHdNVaCRK5d5KeMHh"
        address = ss58_encode(keypair[0], 2)

        self.assertTrue(address == expected_address)
