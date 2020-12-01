# LocalCoinSwap non-custodial Substrate integration.

## __Prelude: Peer-to-peer (P2P) vs centralized exchanges__

Readers will likely be immediately familiar with the lines and charts offered on a typical exchange. A typical exchange maintains an orderbook of *bids* and *asks*, and automatically executes trades by matching buyers and sellers whenever bidding and asking prices collide. Trading on typical exchanges focuses around high-speed execution, and price speculation. It is not uncommon to see additional derivative features on offer such as margin lending, or contracts-for-difference (CFD's) aimed at technical analysis day traders.

```
"The root problem with conventional currency is all the trust required to make it work."
- Satoshi nakomoto
```

Centralized exchanges are such named as they provide a central point in which local currency is aggregated. They maintain bank account which users wire funds to, and receive funds from. Although some are decentralized, most also aggregate the cryptocurrency of their users into company-owned wallets. Trading on a centralised exchange involves sending your funds to the exchange, and trusting that they will be kept safe on your behalf.

Not surprisingly, centralised exchanges raise important questions as regards privacy and security, as well as the growing corporate monopolisation of a cultural space whose ethos centers around decentralization.

Many have been the victim of hacking or large scale theft, and many users have had their local currency seized or frozen for various reasons ranging from accusations of criminality, to simple inability to provide sufficient documentation to satisfy regulatory agencies.

Centralised exchanges also have stringent KYC requirements, which require users to send personal identity documentation to the exchange. In the past there have been leaks of this information - leaving users of the exchange susceptible to identity theft.

A peer-to-peer exchange provides no central aggregation of local currency. In a style akin to eBay, traders on the exchange create advertisements (called offers) which indicate which cryptocurrency they wish to buy or sell. Other traders contact them, and the exchange acts only to safeguard the process of users trading with each other - by providing an escrow service for the cryptocurrency being traded.

By decentralizing the local currency funds, the peer-to-peer exchange has no ability to seize the fiat currency of users. Most importantly however, a peer-to-peer exchange enables large-scale accessibility of cryptocurrency to mainstream users in a way impossible for a centralized exchange to match.

The requirement of centralized exchanges to maintain bank accounts requires them to be heavily restrictive on which payment methods they can offer, and which locations they can accept users.

A peer-to-peer exchange, on the other hand, can support trading using any traditional payment method, in any location of the world.

Over the course of this document, I will demonstrate a way in which Kusama can be integrated on a peer-to-peer exchange, with no need for the end user to hand over their private keys.

I will show the cryptography underlining the process in a proof-of-concept fashion, and back this document up with tests for each individual process.



```python
# Import statements for document
import binascii
import nest_asyncio
from scalecodec.base import ScaleDecoder
from substrateinterface.utils.hasher import blake2_256
from substrateinterface.utils.ss58 import ss58_encode
from substrateinterface.utils.ss58 import ss58_decode
from substrateinterface import SubstrateInterface

import settings
from bindings import bip39
from bindings import sr25519
from bindings import multisig
from ksmref import utils

#Setup helper library
substrate = SubstrateInterface(
    url=settings.NODE_URL, address_type=2, type_registry_preset="kusama")
nest_asyncio.apply()
substrate.init_runtime(block_hash=None)
genesis_hash = substrate.get_block_hash(0)
```

## Part 1: The signup process

When a user signs up to LocalCoinSwap, a 24 word *mnemonic phrase* is generated in their browser. This mnemonic phrase is encrypted with the users password, and stored on our backend. We do not know the users passwords, as they are hashed prior to login, so we are also unable to decrypt the users mnemonic phrase.

When a user logs in, the mnemonic phrase is sent to the browser and decrypted. It is then used as the basis for their wallet addresses, and the signing of transactions. This is similar to many popular web-based wallets.

Users can export their mnemonic phrase, and thus recover funds contained on the associated addresses outside of the exchange.

For the purposes of this generation, I have written bindings to the rust modules which handle BIP39 and the sr25519 algorithm. In production, this functionality will be handled more simply by the Polkadot JS keypair module on the frontend.


```python
example_mnemonic = (
    "boy impose motor jump pear car"
    " pet exact gravity section amazing marble"
    " exit trim two doctor depart rose"
    " guitar injury today stock fruit surface"
)

seed_bytes = bip39.bip39_to_mini_secret(example_mnemonic, "")
seed_hex = bytearray(seed_bytes).hex()

keypair = sr25519.pair_from_seed(bytes.fromhex(seed_hex))

public_key = keypair[0].hex()
private_key = keypair[1].hex()
address = ss58_encode(keypair[0], 2)

print(f"Raw seed from 24 word mnemonic:\n{seed_hex}")
print(f"\nPublic key:\n{public_key}")
print(f"\nPrivate key:\n{private_key}")
print(f"\nKusama address:\n{address}")
```

    Raw seed from 24 word mnemonic:
    64c29cbfc0cec793d1c62a5d80261aa8a1c03535379cedbb0601c1f89ad2271e
    
    Public key:
    026cb1657e60212226cc8001b9c7eece72e58c5a218138ee93797a8ce38a1317
    
    Private key:
    dcfcd70c4095ac286c8c6390bece547b6724ff0569040ae7420bb30f9022e10bcd1fd45de0e527ef2a4ede9a7aeb28d7f90fcf0246d3ce0549939607d38f076a
    
    Kusama address:
    CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo


## Part 2: Overview of the trade

A trade on LocalCoinSwap has 3 participants: the buyer, the seller, and the arbitrator.

It's important at this point to distinguish also between the creator of the trade offer (the *maker*), and the responder to the trade offer (the *taker*). A seller can be a maker or a taker of a trade offer, as can the buyer.

The most intuitive trade example involves the seller as the maker, and the buyer as the taker. The seller signs up to LocalCoinSwap, and then creates an offer which advertise their desire to sell Kusama. The offer will specify terms and conditions of potential trades, such as the price, payment method, and location.

The buyer also signs up to the platform, and responds to the sellers offer to create a *trade request*. Once the seller accepts the request, the trade begins.

At this point a Kusama multisignature address is generated, using the addresses of the buyer, seller, and arbitrator. The seller prepares a transactions and places the funds in the multisignature escrow address.

The buyer then pays the seller directly according to the conditions of the offer.

After receiving payment, the seller then performs a special Kusama *approveAsMulti* transaction. This transaction specifies that they are giving permission for funds to travel from the escrow address to the buyer.

As the address is multisignature, a second approval is required. The buyer has no Kusama yet to create a second approval, so instead the arbitrator performs a Kusama *asMulti* transaction, giving the second lot of approval.

At this point the funds move automatically from the escrow address to the buyer, and the trade is complete. Feedback will be exchanged, and both parties move on - the buyer in posession of the Kusama, and the seller in posession of the local currency.

Because the funds are in a multisignature address requiring 2/3 approval, and only the seller possesses his/her private keys, it is impossible for LocalCoinSwap to steal the funds from the users on the platform. It is also impossible for one party to defraud the other and escape with the cryptocurrency, because in a dispute the arbitrator can decide who receives the cryptocurrency.

Following this abstract, I will demonstrate in full the blockchain functionality involved in conducting such a non-custodial trade.

I will then cover all possible edge-case situations, such as disputes between the buyer and seller, or cancellation requests.

Furthermore, I will demonstrate related cryptography required in the running of an exchange, such as gathering fee information, checking validity of published transactions, and dealing with error situations.

## Part 3: Starting a trade and generating the address

First we get the addresses of the trade participants, and then convert them to account ID's.

We then perform an ascending numerical sort before using our Rust binding to create the multisignature account ID.

Finally we convert this multi-signature account ID into a Kusama address.

This multi-signature address is now the basis of the trade betweent the 3 participants.


```python
# Example addresses used to construct a multisig
buyer_addr = "CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo"
seller_addr = "J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc"
admin_addr = "HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2"

def kusama_addr_to_account_id(address):
    decoded_addr = ss58_decode(address)
    return bytes.fromhex(decoded_addr)

buyer_id = kusama_addr_to_account_id(buyer_addr)
seller_id = kusama_addr_to_account_id(seller_addr)
admin_id = kusama_addr_to_account_id(admin_addr)

# Kusama protocol requires ascending numerical sort of account ID's
trade_addresses = sorted([buyer_id, seller_id, admin_id])

escrow_addr = multisig.multi_account_id(trade_addresses, 2)
escrow_addr = ss58_encode(bytearray(escrow_addr).hex(), 2)

print(f"\nMulti-signature escrow address:\n{escrow_addr}")
```

    
    Multi-signature escrow address:
    HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt


## Part 4: Sending funds into the escrow address

The seller must now place the Kusama in the multisignature escrow address.

To do this we gather some information on Blockchain fees, before constructing a *transfer* call from the wallet of the seller, into the escrow address.

This call is broadcast and published to the Kusama blockchain.

The buyer now verifies that the Kusama has been placed into escrow. In the Kusama network verifying escrow funding is relatively simple, requiring only a balance check of the escrow address. We will show this step for the sake of concept completeness.


```python
# Crucial variables for the trade
seller_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.seller_hexseed))
buyer_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.buyer_hexseed))
arbitrator_keypair = sr25519.pair_from_seed(bytes.fromhex(settings.admin_hexseed))

seller_address = ss58_encode(seller_keypair[0], 2)
buyer_address = ss58_encode(buyer_keypair[0], 2)
arbitrator_address = ss58_encode(arbitrator_keypair[0], 2)

seller_priv = seller_keypair[1].hex()
seller_pub = ss58_decode(seller_address)
arbitrator_priv = arbitrator_keypair[1].hex()
arbitrator_pub = ss58_decode(arbitrator_address)
buyer_priv = buyer_keypair[1].hex()
buyer_pub = ss58_decode(buyer_address)

# We'll consider this as a standard trade value
trade_value = 10000000000
```


```python
# To gather useful fee information, we use examples of signed extrinsics of a known length
simple_transfer = (
    "0x2d0284dee35cf94a50737fc2f3c60439e8bae056aabdcde99de4f2"
    "d37a5f5957bcec4b01b24406f04393e57af7d7f0dc0332c0a47af5a5"
    "8e4d1ed7f85448d3f0dee135361b720f4da59152e94c447ca43afb4d"
    "f676af89f1c8c3625fd29e33357099bf8f006c000400dee35cf94a50"
    "737fc2f3c60439e8bae056aabdcde99de4f2d37a5f5957bcec4b0228"
    "6bee"
)


fee_info = await utils.node_rpc_call("payment_queryInfo", [simple_transfer], 1)
fee_info = fee_info[0].get('result')
print(f"\nFee information for a generic transaction:\n{fee_info}")

call = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)

call.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": settings.escrow_address,
            "value": trade_value,
        },
    }
)

response = substrate.get_runtime_state(
    "System", "Account", [seller_address]
)
assert response.get("result")
nonce = response["result"].get("nonce", 0)


# Create signature payload
signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")

signature_payload.encode(
    {
        "call": str(call.data),
        "era": "00",
        "nonce": nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

data = str(signature_payload.data)
data = bytes.fromhex(data[2:])

signature = sr25519.sign(
    (bytes.fromhex(seller_pub), bytes.fromhex(seller_priv)), data
)

signature = "0x{}".format(signature.hex())

# Create extrinsic
extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder
)

extrinsic.encode(
    {
        "account_id": "0x" + seller_pub,
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

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(extrinsic.data)]
)

extrinsic_hash = utils.get_extrinsic_hash(str(extrinsic.data))
extrinsic_time_point = utils.get_time_point(response, extrinsic_hash)
events = utils.get_extrinsic_events(extrinsic_time_point)
escrow_balance = utils.get_balance_for_address(settings.escrow_address).get("free")

print(f"\nTransaction time point:\n{extrinsic_time_point}")
print(f"\nTransaction hash:\n{extrinsic_hash}")
```

    
    Fee information for a generic transaction:
    {'class': 'normal', 'partialFee': '1000000000', 'weight': 195000000}
    
    Transaction time point:
    (2419844, 3)
    
    Transaction hash:
    0x6bc4780252125e7627548d65a032128eb580a26a5f6a61cc17742bc6c2329a82


## Part 5: Seller acknowledges receipt of funds

Safe in the knowledge that the Kusama is in escrow, the buyer now makes a direct local currency transfer to the seller.

Once the seller has received the payment, they then make an *approveAsMulti* call to the Kusama blockchain. This call wraps the hash of a transfer call to the buyers address.

This call acknowledges the sellers desire to finalise the escrow in the buyers favour.

The seller also makes a second *approveAsMulti* call, which acknowledges the trading fee given to the arbitrator.

The trading fee is 1% of the value of the trade, and rewards the arbitrator for their role in safeguarding the escrow process, and paying to relay calls.


```python
# Prepare in advance the reusable calls
buyer_transfer = ScaleDecoder.get_decoder_class("Call", metadata=substrate.metadata_decoder)
fee_transfer = ScaleDecoder.get_decoder_class("Call", metadata=substrate.metadata_decoder)

trade_fee = int(0.01 * trade_value)
trade_amount = trade_value - trade_fee

buyer_transfer.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": buyer_address,
            "value": trade_amount,
        },
    })
fee_transfer.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": arbitrator_address,
            "value": trade_fee,
        },
    })

print(f"Total trade is for {trade_value}\nTotal fees (1%) are {trade_fee}\nBuyer will receive {trade_amount}\n")

```

    Total trade is for 10000000000
    Total fees (1%) are 100000000
    Buyer will receive 9900000000
    



```python
def hash_call(call):
    call = bytes.fromhex(str(call.data)[2:])
    return f"0x{blake2_256(call)}"

hashed_buyer_transfer = hash_call(buyer_transfer)
hashed_fee_transfer = hash_call(fee_transfer)

buyer_transfer_approve_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)
fee_transfer_approve_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

buyer_transfer_approve_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "approve_as_multi",
        "call_args": {
            "call_hash": hashed_buyer_transfer,
            "maybe_timepoint": None,
            "other_signatories": sorted(
                [arbitrator_address, buyer_address]
            ),
            "threshold": 2,
        },
    })
fee_transfer_approve_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "approve_as_multi",
        "call_args": {
            "call_hash": hashed_fee_transfer,
            "maybe_timepoint": None,
            "other_signatories": sorted(
                [arbitrator_address, buyer_address]
            ),
            "threshold": 2,
        },
    })

response = substrate.get_runtime_state(
    "System", "Account", [seller_address]
)
assert response.get("result")
seller_address_nonce = response["result"].get("nonce", 0)

buyer_transfer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
buyer_transfer_signature_payload.encode(
    {
        "call": str(buyer_transfer_approve_as_multi.data),
        "era": "00",
        "nonce": seller_address_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    })

fee_transfer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
fee_transfer_signature_payload.encode(
    {
        "call": str(fee_transfer_approve_as_multi.data),
        "era": "00",
        "nonce": seller_address_nonce + 1,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    })

# Sign payloads
data = str(buyer_transfer_signature_payload.data)
data = bytes.fromhex(data[2:])
signature = sr25519.sign(
    (bytes.fromhex(seller_pub), bytes.fromhex(seller_priv)), data)
buyer_transfer_signature = "0x{}".format(signature.hex())

data = str(fee_transfer_signature_payload.data)
data = bytes.fromhex(data[2:])
signature = sr25519.sign(
    (bytes.fromhex(seller_pub), bytes.fromhex(seller_priv)), data)
fee_transfer_signature = "0x{}".format(signature.hex())


# Create extrinsics
buyer_transfer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)
fee_transfer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

buyer_transfer_extrinsic.encode(
    {
        "account_id": "0x" + seller_pub,
        "signature_version": 1,
        "signature": buyer_transfer_signature,
        "call_function": buyer_transfer_approve_as_multi.value["call_function"],
        "call_module": buyer_transfer_approve_as_multi.value["call_module"],
        "call_args": buyer_transfer_approve_as_multi.value["call_args"],
        "nonce": seller_address_nonce,
        "era": "00",
        "tip": 0,
    })
fee_transfer_extrinsic.encode(
    {
        "account_id": "0x" + seller_pub,
        "signature_version": 1,
        "signature": fee_transfer_signature,
        "call_function": fee_transfer_approve_as_multi.value["call_function"],
        "call_module": fee_transfer_approve_as_multi.value["call_module"],
        "call_args": fee_transfer_approve_as_multi.value["call_args"],
        "nonce": seller_address_nonce + 1,
        "era": "00",
        "tip": 0,
    })

# Broadcast both transactions and gather timepoints
response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(buyer_transfer_extrinsic.data)]
)
buyer_transfer_extrinsic_hash = utils.get_extrinsic_hash(str(buyer_transfer_extrinsic.data))
buyer_transfer_extrinsic_time_point = utils.get_time_point(response, buyer_transfer_extrinsic_hash)

print(f"\nBuyer transfer approveAsMulti time point:\n{buyer_transfer_extrinsic_time_point}")
print(f"\nTransaction hash:\n{buyer_transfer_extrinsic_hash}")

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(fee_transfer_extrinsic.data)]
)

fee_transfer_extrinsic_hash = utils.get_extrinsic_hash(str(fee_transfer_extrinsic.data))
fee_transfer_extrinsic_time_point = utils.get_time_point(response, fee_transfer_extrinsic_hash)

print(f"\nFee transfer approveAsMulti time point:\n{fee_transfer_extrinsic_time_point}")
print(f"\nTransaction hash:\n{fee_transfer_extrinsic_hash}")
```

    
    Buyer transfer approveAsMulti time point:
    (2419870, 3)
    
    Transaction hash:
    0x627caa997206e639093049f71617d380b9fa1477d137288031ea7944415aff29
    
    Fee transfer approveAsMulti time point:
    (2419873, 3)
    
    Transaction hash:
    0x6cf4f11e24f8482b92520e72b5ceb49330c9f949fde899a24b6f096c652ee460


## Part 6: Arbitrator finalizes trade

The multi-signature trade can now be completed, and publishing extrinsics to the Kusama blockchain requires payment in Kusama. However, the buyer does not possess any Kusama with which to make the transaction.

To handle this, we instead have the arbitrator make the final call on their behalf.

The arbitrator now constructs two *asMulti* calls, the first to finalise the escrow, and the second to receive the fee. Crucially, the timepoints of each of these calls must refer to the earlier *approveAsMulti* calls.

These calls wrap the same transfer call used earlier to create the hash.


```python
buyer_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)
buyer_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "as_multi",
        "call_args": {
            "call": buyer_transfer.serialize(),
            "maybe_timepoint": {
                "height": buyer_transfer_extrinsic_time_point[0],
                "index": buyer_transfer_extrinsic_time_point[1],
            },
            "other_signatories": sorted(
                [buyer_address, seller_address]
            ),
            "threshold": 2,
        },
})
fee_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)
fee_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "as_multi",
        "call_args": {
            "call": fee_transfer.serialize(),
            "maybe_timepoint": {
                "height": fee_transfer_extrinsic_time_point[0],
                "index": fee_transfer_extrinsic_time_point[1],
            },
            "other_signatories": sorted(
                [buyer_address, seller_address]
            ),
            "threshold": 2,
        },
})

response = substrate.get_runtime_state(
    "System", "Account", [arbitrator_address]
)
assert response.get("result")
arbitrator_nonce = response["result"].get("nonce", 0)

# Create signature payload
buyer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
buyer_signature_payload.encode(
    {
        "call": str(buyer_as_multi.data),
        "era": "00",
        "nonce": arbitrator_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

fee_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
fee_signature_payload.encode(
    {
        "call": str(fee_as_multi.data),
        "era": "00",
        "nonce": arbitrator_nonce + 1,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

# Sign payload
data = str(buyer_signature_payload.data)
data = bytes.fromhex(data[2:])

signature = sr25519.sign(
    (bytes.fromhex(arbitrator_pub), bytes.fromhex(arbitrator_priv)), data)

buyer_signature = "0x{}".format(signature.hex())

data = str(fee_signature_payload.data)
data = bytes.fromhex(data[2:])

signature = sr25519.sign(
    (bytes.fromhex(arbitrator_pub), bytes.fromhex(arbitrator_priv)), data)

fee_signature = "0x{}".format(signature.hex())

# Create extrinsic
buyer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)
fee_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

buyer_extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
        "signature_version": 1,
        "signature": buyer_signature,
        "call_function": buyer_as_multi.value["call_function"],
        "call_module": buyer_as_multi.value["call_module"],
        "call_args": buyer_as_multi.value["call_args"],
        "nonce": arbitrator_nonce,
        "era": "00",
        "tip": 0,
    }
)

fee_extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
        "signature_version": 1,
        "signature": fee_signature,
        "call_function": fee_as_multi.value["call_function"],
        "call_module": fee_as_multi.value["call_module"],
        "call_args": fee_as_multi.value["call_args"],
        "nonce": arbitrator_nonce + 1,
        "era": "00",
        "tip": 0,
    }
)


response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(buyer_extrinsic.data)]
)

buyer_extrinsic_hash = utils.get_extrinsic_hash(str(buyer_extrinsic.data))
buyer_extrinsic_time_point = utils.get_time_point(response, buyer_extrinsic_hash)

print(f"\nArbitrator as_multi time point:\n{buyer_extrinsic_time_point}")
print(f"\nas_multi hash:\n{buyer_extrinsic_hash}")

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(fee_extrinsic.data)]
)

fee_extrinsic_hash = utils.get_extrinsic_hash(str(fee_extrinsic.data))
fee_extrinsic_time_point = utils.get_time_point(response, fee_extrinsic_hash)

print(f"\nArbitrator fee as_multi time point:\n{fee_extrinsic_time_point}")
print(f"\nas_multi fee hash:\n{fee_extrinsic_hash}")
```

    
    Arbitrator as_multi time point:
    (2419892, 3)
    
    as_multi hash:
    0x0a428c476dc9e055c3d8d3f849d619498171591e500b946ad897530201ca6abc
    
    Arbitrator fee as_multi time point:
    (2419896, 3)
    
    as_multi fee hash:
    0xdc31a57accc0b6d787e273e400cc604b190394e9e702139d669319d5b2eeac27


## Part 7: Cancelling a trade

In this situation the Kusama has been placed in escrow, and both parties consent to the cancellation of the trade, and thus the return of the funds to the seller.

As in the standard trade, we publish two transactions to the Blockchain, the first an approveAsMulti call for the transfer back to the seller, and the second asMulti call published by the arbitrator.

In this situation no fee is charged by the arbitrator. For the sake of cluttering the code less, we will not show the fee transaction in this situation.


```python
seller_transfer = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

# In this case the dest is back to the seller_address
seller_transfer.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": seller_address,
            "value": trade_value,
        },
    })


def hash_call(call):
    call = bytes.fromhex(str(call.data)[2:])
    return f"0x{blake2_256(call)}"

hashed_seller_transfer = hash_call(seller_transfer)

seller_transfer_approve_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

seller_transfer_approve_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "approve_as_multi",
        "call_args": {
            "call_hash": hashed_seller_transfer,
            "maybe_timepoint": None,
            "other_signatories": sorted(
                [arbitrator_address, buyer_address]
            ),
            "threshold": 2,
        },
    })

response = substrate.get_runtime_state(
    "System", "Account", [seller_address]
)
assert response.get("result")
seller_address_nonce = response["result"].get("nonce", 0)

seller_transfer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
seller_transfer_signature_payload.encode(
    {
        "call": str(seller_transfer_approve_as_multi.data),
        "era": "00",
        "nonce": seller_address_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    })

# Sign payloads
data = str(seller_transfer_signature_payload.data)
data = bytes.fromhex(data[2:])
signature = sr25519.sign(
    (bytes.fromhex(seller_pub), bytes.fromhex(seller_priv)), data)
seller_transfer_signature = "0x{}".format(signature.hex())

# Create extrinsics
seller_transfer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

seller_transfer_extrinsic.encode(
    {
        "account_id": "0x" + seller_pub,
        "signature_version": 1,
        "signature": seller_transfer_signature,
        "call_function": seller_transfer_approve_as_multi.value["call_function"],
        "call_module": seller_transfer_approve_as_multi.value["call_module"],
        "call_args": seller_transfer_approve_as_multi.value["call_args"],
        "nonce": seller_address_nonce,
        "era": "00",
        "tip": 0,
    })

# Broadcast transaction and gather timepoint

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(seller_transfer_extrinsic.data)]
)
seller_transfer_extrinsic_hash = utils.get_extrinsic_hash(str(seller_transfer_extrinsic.data))
seller_transfer_extrinsic_time_point = utils.get_time_point(response, seller_transfer_extrinsic_hash)

print(f"\nSeller transfer approveAsMulti time point:\n{seller_transfer_extrinsic_time_point}")
print(f"\nTransaction hash:\n{seller_transfer_extrinsic_hash}")


####################################################################################
# We call asMulti like before. In this case we want to transfer back to the seller #
####################################################################################


seller_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)
seller_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "as_multi",
        "call_args": {
            "call": seller_transfer.serialize(),
            "maybe_timepoint": {
                "height": seller_transfer_extrinsic_time_point[0],
                "index": seller_transfer_extrinsic_time_point[1],
            },
            "other_signatories": sorted(
                [buyer_address, seller_address]
            ),
            "threshold": 2,
        },
})

response = substrate.get_runtime_state(
    "System", "Account", [arbitrator_address]
)
assert response.get("result")
arbitrator_nonce = response["result"].get("nonce", 0)

# Create signature payload
seller_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
seller_signature_payload.encode(
    {
        "call": str(seller_as_multi.data),
        "era": "00",
        "nonce": arbitrator_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

# Sign payload
data = str(seller_signature_payload.data)
data = bytes.fromhex(data[2:])

seller_signature_payload = sr25519.sign(
    (bytes.fromhex(arbitrator_pub), bytes.fromhex(arbitrator_priv)), data)

seller_signature_payload = "0x{}".format(seller_signature_payload.hex())

# Create extrinsic
seller_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

seller_extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
        "signature_version": 1,
        "signature": seller_signature_payload,
        "call_function": seller_as_multi.value["call_function"],
        "call_module": seller_as_multi.value["call_module"],
        "call_args": seller_as_multi.value["call_args"],
        "nonce": arbitrator_nonce,
        "era": "00",
        "tip": 0,
    }
)

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(seller_extrinsic.data)]
)

seller_extrinsic_hash = utils.get_extrinsic_hash(str(seller_extrinsic.data))
seller_extrinsic_time_point = utils.get_time_point(response, seller_extrinsic_hash)

print(f"\nArbitrator transfer as_multi time point:\n{seller_extrinsic_time_point}")
print(f"\nTransaction hash:\n{seller_extrinsic_hash}")
```

    
    Seller transfer approveAsMulti time point:
    (2419904, 3)
    
    Transaction hash:
    0xa7be218d0e74cca0510f5763812e3a3952768d774ca822795c9e61bdd289e284
    
    Arbitrator transfer as_multi time point:
    (2419908, 2)
    
    Transaction hash:
    0x10efdb3d318a5b16bdc30f16d068279cee84f0df004a28728b22b1269060f3d0


## Part 8: Disputes between the buyer and seller

In this situation the buyer and seller has come to a disagreement about the rightful owner of the funds. Either the buyer or seller raises a *dispute ticket*, and asks the arbitrator to come to a decision about the rightful owner of the funds.

In the situation where the arbitrator decides that the seller is the rightful owner, the transaction flow is the same as in the cancellation example.

However, in the event that the buyer is the rightful owner, it can be assumed that the seller will be unwilling to publish an *approveAsMulti* transaction on the buyers behalf.

Therefore, the arbitrator prepares three transactions.

The first transaction is the simple transfer of a small amount of funds to the buyer, in order that they can pay for transaction fees.

The second transaction is an *approveAsMulti* call for the fee which is paid to the arbitrator.

The third transaction is an *approveAsMulti* call for the rest of the funds to travel to the buyer.

The arbitrator publishes the first two transactions, and then awaits the buyer to publish an *asMulti* transaction for the fee.

Once this occurs, the arbitrator publishes the final transaction, and the buyer then also finalises this with their own *asMulti* transaction.


```python
#########################################################################################
# The first transaction is the simple transfer of a small amount of funds to the buyer, #
# in order that they can pay for transaction fees.                                      #
#########################################################################################


# We'll consider this as the fee value for the 2 asMulti calls for fee to be sent to 
# the arbitrator and the rest of the funds to travel to the buyer
dispute_fee_value = 2000000000

call = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)

call.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": buyer_address,
            "value": dispute_fee_value,
        },
    }
)

response = substrate.get_runtime_state(
    "System", "Account", [arbitrator_address]
)
assert response.get("result")
nonce = response["result"].get("nonce", 0)

# Create signature payload
signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
signature_payload.encode(
    {
        "call": str(call.data),
        "era": "00",
        "nonce": nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

data = str(signature_payload.data)
data = bytes.fromhex(data[2:])

signature = sr25519.sign(
    (bytes.fromhex(arbitrator_pub), bytes.fromhex(arbitrator_priv)), data
)

signature = "0x{}".format(signature.hex())

# Create extrinsic
extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder
)

extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
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

response = utils.rpc_subscription(
    "author_submitAndWatchExtrinsic",
    [str(extrinsic.data)],
    substrate.request_id,
    settings.NODE_URL,
)

extrinsic_hash = utils.get_extrinsic_hash(str(extrinsic.data))
extrinsic_time_point = utils.get_time_point(response, extrinsic_hash)
events = utils.get_extrinsic_events(extrinsic_time_point)
buyer_balance = utils.get_balance_for_address(buyer_address).get("free")

print(f"\nTransaction time point:\n{extrinsic_time_point}")
print(f"\nTransaction hash:\n{extrinsic_hash}")
print(f"\nEvents returned from published transaction:\n{events}")

###############################################################################################
# Second transaction is an *approveAsMulti* call for the fee which is paid to the arbitrator. #
###############################################################################################

fee_transfer = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

trade_fee = int(0.01 * trade_value)
trade_amount = trade_value - trade_fee

print(f"Total trade is for {trade_value}\nTotal fees (1%) are {trade_fee}\nBuyer will receive {trade_amount}\n")


fee_transfer.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": arbitrator_address,
            "value": trade_fee,
        },
    })

def hash_call(call):
    call = bytes.fromhex(str(call.data)[2:])
    return f"0x{blake2_256(call)}"

hashed_fee_transfer = hash_call(fee_transfer)

fee_transfer_approve_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

fee_transfer_approve_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "approve_as_multi",
        "call_args": {
            "call_hash": hashed_fee_transfer,
            "maybe_timepoint": None,
            "other_signatories": sorted(
                [seller_address, buyer_address]
            ),
            "threshold": 2,
        },
    })

response = substrate.get_runtime_state(
    "System", "Account", [arbitrator_address]
)
assert response.get("result")
arbitrator_address_nonce = response["result"].get("nonce", 0)

fee_transfer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
fee_transfer_signature_payload.encode(
    {
        "call": str(fee_transfer_approve_as_multi.data),
        "era": "00",
        "nonce": arbitrator_address_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    })

# Sign payloads

data = str(fee_transfer_signature_payload.data)
data = bytes.fromhex(data[2:])
signature = sr25519.sign(
    (bytes.fromhex(arbitrator_pub), bytes.fromhex(arbitrator_priv)), data)
fee_transfer_signature = "0x{}".format(signature.hex())


# Create extrinsics
fee_transfer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

fee_transfer_extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
        "signature_version": 1,
        "signature": fee_transfer_signature,
        "call_function": fee_transfer_approve_as_multi.value["call_function"],
        "call_module": fee_transfer_approve_as_multi.value["call_module"],
        "call_args": fee_transfer_approve_as_multi.value["call_args"],
        "nonce": arbitrator_address_nonce,
        "era": "00",
        "tip": 0,
    })

# Broadcast transaction and gather timepoint
response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(fee_transfer_extrinsic.data)]
)

fee_transfer_extrinsic_hash = utils.get_extrinsic_hash(str(fee_transfer_extrinsic.data))
fee_transfer_extrinsic_time_point = utils.get_time_point(response, fee_transfer_extrinsic_hash)


print(f"\nBuyer transfer approveAsMulti time point:\n{fee_transfer_extrinsic_time_point}")
print(f"\nTransaction hash:\n{fee_transfer_extrinsic_hash}")

################################################################################
# Arbitrator awaits the buyer to publish an *asMulti* transaction for the fee. #
################################################################################

fee_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)
fee_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "as_multi",
        "call_args": {
            "call": fee_transfer.serialize(),
            "maybe_timepoint": {
                "height": fee_transfer_extrinsic_time_point[0],
                "index": fee_transfer_extrinsic_time_point[1],
            },
            "other_signatories": sorted(
                [arbitrator_address, seller_address]
            ),
            "threshold": 2,
        },
})

response = substrate.get_runtime_state(
    "System", "Account", [buyer_address]
)
assert response.get("result")
buyer_nonce = response["result"].get("nonce", 0)

# Create signature payload
fee_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")

fee_signature_payload.encode(
    {
        "call": str(fee_as_multi.data),
        "era": "00",
        "nonce": arbitrator_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

# Sign payload
data = str(fee_signature_payload.data)
data = bytes.fromhex(data[2:])

signature = sr25519.sign(
    (bytes.fromhex(buyer_pub), bytes.fromhex(buyer_priv)), data)

fee_signature = "0x{}".format(signature.hex())

# Create extrinsic
fee_extrinsic.encode(
    {
        "account_id": "0x" + buyer_pub,
        "signature_version": 1,
        "signature": fee_signature,
        "call_function": fee_as_multi.value["call_function"],
        "call_module": fee_as_multi.value["call_module"],
        "call_args": fee_as_multi.value["call_args"],
        "nonce": arbitrator_nonce,
        "era": "00",
        "tip": 0,
    }
)

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(fee_extrinsic.data)]
)

fee_extrinsic_hash = utils.get_extrinsic_hash(str(fee_extrinsic.data))
fee_extrinsic_time_point = utils.get_time_point(response, fee_extrinsic_hash)

print(f"\nBuyer fee as_multi time point:\n{fee_extrinsic_time_point}")
print(f"\nas_multi fee hash:\n{fee_extrinsic_hash}")

################################################################################
# Now that the fees are handled the arbitrator publishes the final transaction #
################################################################################

buyer_transfer = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

buyer_transfer.encode(
    {
        "call_module": "Balances",
        "call_function": "transfer",
        "call_args": {
            "dest": buyer_address,
            "value": trade_amount,
        },
    })

hashed_buyer_transfer = hash_call(buyer_transfer)

buyer_transfer_approve_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder)

buyer_transfer_approve_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "approve_as_multi",
        "call_args": {
            "call_hash": hashed_buyer_transfer,
            "maybe_timepoint": None,
            "other_signatories": sorted(
                [seller_address, buyer_address]
            ),
            "threshold": 2,
        },
    })

response = substrate.get_runtime_state(
    "System", "Account", [arbitrator_address]
)
assert response.get("result")
arbitrator_address_nonce = response["result"].get("nonce", 0)


buyer_transfer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")
buyer_transfer_signature_payload.encode(
    {
        "call": str(buyer_transfer_approve_as_multi.data),
        "era": "00",
        "nonce": arbitrator_address_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    })

# Sign payloads
data = str(buyer_transfer_signature_payload.data)
data = bytes.fromhex(data[2:])
signature = sr25519.sign(
    (bytes.fromhex(arbitrator_pub), bytes.fromhex(arbitrator_priv)), data)
buyer_transfer_signature = "0x{}".format(signature.hex())

# Create extrinsics
buyer_transfer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

buyer_transfer_extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
        "signature_version": 1,
        "signature": buyer_transfer_signature,
        "call_function": buyer_transfer_approve_as_multi.value["call_function"],
        "call_module": buyer_transfer_approve_as_multi.value["call_module"],
        "call_args": buyer_transfer_approve_as_multi.value["call_args"],
        "nonce": arbitrator_address_nonce,
        "era": "00",
        "tip": 0,
    })

# Broadcast transaction and gather timepoint

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(buyer_transfer_extrinsic.data)]
)
buyer_transfer_extrinsic_hash = utils.get_extrinsic_hash(str(buyer_transfer_extrinsic.data))
buyer_transfer_extrinsic_time_point = utils.get_time_point(response, buyer_transfer_extrinsic_hash)

print(f"\nBuyer transfer approveAsMulti time point:\n{buyer_transfer_extrinsic_time_point}")
print(f"\nTransaction hash:\n{buyer_transfer_extrinsic_hash}")

####################################################################
# Buyer now finalises dispute with their own *asMulti* transaction #
####################################################################

buyer_as_multi = ScaleDecoder.get_decoder_class(
    "Call", metadata=substrate.metadata_decoder
)
buyer_as_multi.encode(
    {
        "call_module": "Utility",
        "call_function": "as_multi",
        "call_args": {
            "call": buyer_transfer.serialize(),
            "maybe_timepoint": {
                "height": buyer_transfer_extrinsic_time_point[0],
                "index": buyer_transfer_extrinsic_time_point[1],
            },
            "other_signatories": sorted(
                [arbitrator_address, seller_address]
            ),
            "threshold": 2,
        },
})

response = substrate.get_runtime_state(
    "System", "Account", [buyer_address]
)
assert response.get("result")
buyer_address_nonce = response["result"].get("nonce", 0)


# Create signature payload

buyer_signature_payload = ScaleDecoder.get_decoder_class("ExtrinsicPayloadValue")

buyer_signature_payload.encode(
    {
        "call": str(buyer_as_multi.data),
        "era": "00",
        "nonce": buyer_address_nonce,
        "tip": 0,
        "specVersion": substrate.runtime_version,
        "genesisHash": genesis_hash,
        "blockHash": genesis_hash,
    }
)

# Sign payload
data = str(buyer_signature_payload.data)
data = bytes.fromhex(data[2:])

signature = sr25519.sign(
    (bytes.fromhex(buyer_pub), bytes.fromhex(buyer_priv)), data)

buyer_signature = "0x{}".format(signature.hex())

# Create extrinsic
buyer_extrinsic = ScaleDecoder.get_decoder_class(
    "Extrinsic", metadata=substrate.metadata_decoder)

buyer_extrinsic.encode(
    {
        "account_id": "0x" + arbitrator_pub,
        "signature_version": 1,
        "signature": buyer_signature,
        "call_function": buyer_as_multi.value["call_function"],
        "call_module": buyer_as_multi.value["call_module"],
        "call_args": buyer_as_multi.value["call_args"],
        "nonce": buyer_address_nonce,
        "era": "00",
        "tip": 0,
    }
)

response = await utils.node_rpc_call(
    "author_submitAndWatchExtrinsic",
    [str(buyer_extrinsic.data)]
)

buyer_extrinsic_hash = utils.get_extrinsic_hash(str(buyer_extrinsic.data))
buyer_extrinsic_time_point = utils.get_time_point(response, buyer_extrinsic_hash)
```

# Part 9: Reference summation

The above code demonstrates the exact steps involved in the non-custodial trading process. However, there are a couple of additional factors which an exchange must take into consideration for an integration. I will go over a few of them:

**Changes to the Kusama blockchain**  
The Kusama blockchain avoids the need for hard forks by having the ability to radicaly change its own runtime codebase. To keep on top of this, it is imperative that our exchange tracks the latest version of the Kusama runtime using the `system_lastRuntimeUpgrade` variable, and runs the tests in this reference each time a codebase change occurs.

**Threshold transaction values**  
The Kusama blockchain requires that the initiating party in a trade have an account balance of `0.3 + 0.05 * threshold` KSM, the threshold in a 3 person multi-signature trade being 2. Therefore, we set a minimum trade value of 1 KSM to safely handle all edge-cases that might occur.

**Diagnostics and resolutions for failed trade transactions**  
For various reasons, an `approveAsMulti` or `asMulti` transaction might fail. Common errors include:

*No timepoint specified, yet the operation is already underway*    
A successfull transaction was already pushed from the same address. The exchange should find the previous transaction, and manually progress the escrow process with the correct timepoint.

*The timepoint refers to a different transaction than the one underway*  
The timepoint being used is incorrect, the trade should be manually progressed after the correct timepoint is found

*Signatories incorrectly sorted*  
A sort command must be run on the signatories list before re-pushing

*Insufficient signatories*  
In this rather deceptive error message the seller has insufficient balance for the trade. The sellers account balance must be increased before the transaction is pushed again.


```python

```
