import binascii

from substrateinterface.utils.ss58 import ss58_decode
from substrateinterface.utils.ss58 import ss58_encode

from bindings import multisig

buyer_addr = "FQ2W1LrE9u6hrgv9bZzy3zq7e3JARRZm3d3UvnMREmAZCBb"
seller_addr = "DUorqgcRkXhpQvfhsXfjSZVNWRJWE5qGo7md53Cpix8BRnb"
admin_addr = "D3JaNpndKAG8PMZnsvsNE7UemYpVs44PB6kCHxW4wNSkxZh"


def kusama_addr_to_account_id(address):
    decoded_addr = ss58_decode(address)
    decoded_addr_bytes = bytes.fromhex(decoded_addr)
    return decoded_addr_bytes


buyer_id = kusama_addr_to_account_id(buyer_addr)
seller_id = kusama_addr_to_account_id(seller_addr)
admin_id = kusama_addr_to_account_id(admin_addr)

trade_addresses = sorted([buyer_id, seller_id, admin_id])

escrow_addr = multisig.multi_account_id(trade_addresses, 2)
escrow_addr = binascii.hexlify(bytearray(escrow_addr)).decode("ascii")
escrow_addr = ss58_encode(escrow_addr, 2)
print(escrow_addr)
