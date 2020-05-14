require('dotenv').config()

export const kusamaNode = 'wss://kusama-rpc.polkadot.io/';
export const threshold = 2;
export const escrowAddress = process.env.ESCROW_ADDRESS;
export const sellerHexSeed = process.env.SELLER_HEX_SEED;
export const adminHexSeed = process.env.ADMIN_HEX_SEED;
export const buyerHexSeed = process.env.BUYER_HEX_SEED;

export const buyerAddress = 'CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo';
export const adminAddress = 'HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2';
export const sellerAddress = 'J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc';
export const tradeValue = 10000000000;
