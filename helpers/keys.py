import binascii

from substrateinterface.utils.ss58 import ss58_decode
from substrateinterface.utils.ss58 import ss58_encode

from bindings import multisig
from bindings import sr25519


def get_escrow_address(addresses: list, *, threshold: int = 2):
    _addresses = []
    for addr in addresses:
        _addr = ss58_decode(addr)
        _addr = bytes.fromhex(_addr)
        _addresses.append(_addr)

    _addresses = sorted(_addresses)
    print(_addresses)
    escrow_addr = multisig.multi_account_id(_addresses, threshold)
    escrow_addr = binascii.hexlify(bytearray(escrow_addr)).decode("ascii")
    return ss58_encode(escrow_addr, 2)


def get_addr_from_seed(seed: str,):
    keypair = sr25519.pair_from_seed(bytes.fromhex(seed))
    return ss58_encode(keypair[0], 2)
