## A non-custodial KSM trade on LocalCoinSwap can have several outcomes

### These examples use the Polkadot JS libraries to demonstrate example trades in which each of the following scenarios occur:

1. Both buyer and seller are happy, money is released from escrow to buyer  
2. Buyer wishes to cancel, funds are returned to seller
3. Seller wishes to cancel, buyer consents, funds are returned to seller
4. Seller wishes to cancel, buyer does not consent, trade continues as normal
5. Buyer is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the buyers favour and the funds are sent to the buyer
6. Buyer is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the sellers favour and the funds are sent to the seller
7. Seller is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the buyers favour and the funds are sent to the buyer
8. Seller is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the sellers favour and the funds are sent to the seller

From a blockchain perspective 2, 3, 6, and 8 are identical in terms of the transactions which occur (seller and admin authorise funds back to seller), these scenarios are contained in the funds_back_to_seller example.

From a blockchain perspective 5 and 7 are also identical, and are contained in the same funds_dispute_to_buyer example. WIP: we will batch these transactions so the buyer does not pay fees.

Note: In scenario 4 nothing happens on the blockchain, and so we do not need an example test either.

To run these tests, (after loading appropriate variables in config), use the following commands:
```
yarn standard_trade
yarn funds_back_to_seller
yarn funds_dispute_to_buyer
```
