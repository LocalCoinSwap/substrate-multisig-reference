import base64
import unittest

from bindings import sr25519


class TestSignAndVerify(unittest.TestCase):
    def test_sign_and_verify(self):
        """Test that we can successfully sign a message"""
        keypair = (
            bytes.fromhex(
                ("026cb1657e60212226cc8001b9c7eec" "e72e58c5a218138ee93797a8ce38a1317")
            ),
            bytes.fromhex(
                (
                    "dcfcd70c4095ac286c8c6390bece547b6724ff0569"
                    "040ae7420bb30f9022e10bcd1fd45de0e527ef2a4e"
                    "de9a7aeb28d7f90fcf0246d3ce0549939607d38f07"
                    "6a"
                )
            ),
        )

        message = base64.b64encode(
            b"it reaches out it reaches out it reaches out it reaches out"
            b"One hundred and thirteen times a second, nothing answers and it"
            b"reaches out. It is not conscious, though parts of it are."
            b"There are structures within it that were once separate"
            b" organisms; aboriginal, evolved, and complex. It is designed to"
            b" improvise, to use what is there and then move on. Good enough "
            b"is good enough, and so the artifacts are ignored or adapted. "
            b"The conscious parts try to make sense of the reaching out."
            b"Try to interpret it."
        )

        sig = sr25519.sign(keypair, message)

        public_key = bytes.fromhex(
            ("026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317")
        )

        message = base64.b64encode(
            b"it reaches out it reaches out it reaches out it reaches out"
            b"One hundred and thirteen times a second, nothing answers and it"
            b"reaches out. It is not conscious, though parts of it are."
            b"There are structures within it that were once separate"
            b" organisms; aboriginal, evolved, and complex. It is designed to"
            b" improvise, to use what is there and then move on. Good enough "
            b"is good enough, and so the artifacts are ignored or adapted. "
            b"The conscious parts try to make sense of the reaching out."
            b"Try to interpret it."
        )

        self.assertTrue(sr25519.verify(sig, message, public_key))

    def test_fail_verify_invalid_signature(self):
        """Test that a invalid signature will fail to verify"""
        public_key = bytes.fromhex(
            "56a1edb23ba39364bca160b3298cfb7ec8c5272af841c59a7160123a7d705c4d"
        )
        sig = bytes.fromhex(
            "bcb041916b70af03b17ed1c622817ffa50815499db"
            "e18895d2f9618fdeadbeef86c69d5a20e04ff66317c7e14d2580dedfc6bbff1"
            "4c380569cad5c02719c420c"
        )

        message = base64.b64encode(
            b"it reaches out it reaches out it reaches out it reaches out"
            b"One hundred and thirteen times a second, nothing answers and it"
            b"reaches out. It is not conscious, though parts of it are."
            b"There are structures within it that were once separate"
            b" organisms; aboriginal, evolved, and complex. It is designed to"
            b" improvise, to use what is there and then move on. Good enough "
            b"is good enough, and so the artifacts are ignored or adapted. "
            b"The conscious parts try to make sense of the reaching out."
            b"Try to interpret it."
        )

        self.assertFalse(sr25519.verify(sig, message, public_key))
