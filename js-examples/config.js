require('dotenv').config()

export const kusamaNode = 'wss://kusama-rpc.polkadot.io/';

// Trade variables
export const sellerHexSeed = process.env.SELLER_HEX_SEED;
export const adminHexSeed = process.env.ADMIN_HEX_SEED;
export const buyerHexSeed = process.env.BUYER_HEX_SEED;
export const buyerAddress = 'CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo';
export const adminAddress = 'HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2';
export const sellerAddress = 'J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc';
export const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';
export const tradeValue = 25000000000;
