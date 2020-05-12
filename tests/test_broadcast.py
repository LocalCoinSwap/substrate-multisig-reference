import unittest
from ksmref import utils


class TestBroadcast(unittest.TestCase):
    def test_broadcast(self):
        """Test that we can broadcast an exctrinsic"""

        extrinsic = "0x390284f68a66c0cd540d7e6ba34d3fa67b40e5eea07ea891265a39e064d39a2375aa3301a08343b68c940a846190bc88eb63dd0222e5c35cbcdc682c4437340f5486c720256280ae8785a7f4df079a351dbb045d4eef4b8fb47780519f3f2d875619f786007101000400dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b0700e40b5402"

        result = utils.broadcast(extrinsic)
        print("result", result)
        self.assertEqual(result[1], True)

