## A non-custodial KSM trade on LocalCoinSwap can have several outcomes

### These examples use the Polkadot JS libraries to demonstrate example trades in which each of the following scenarios occur:

1. Both buyer and seller are happy, money is released from escrow to buyer  
2. Buyer wishes to cancel, funds are returned to seller
3. Seller wishes to cancel, buyer consents, funds are returned to seller
4. Buyer is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the buyers favour and the funds are sent to the buyer
5. Buyer is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the sellers favour and the funds are sent to the seller
6. Seller is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the buyers favour and the funds are sent to the buyer
7. Seller is unhappy with the trade, and raises dispute. LocalCoinSwap rules in the sellers favour and the funds are sent to the seller

Note: there is an additional scenario where seller wishes to cancel, and buyer does not consent. However, in this scenario nothing happens on the blockchain, and so we do not need an example.

To run these tests, (after loading appropriate variables in config), use the following commands:
```
yarn standard_trade
yarn buyer_cancels
yarn seller_cancels
yarn buyer_disputes_wins
yarn buyer_disputes_loses
yarn seller_disputes_wins
yarn seller_disputes_loses
```
