require('dotenv').config()
const { Keyring } = require('@polkadot/keyring');
import { cryptoWaitReady } from '@polkadot/util-crypto';
import {
    encodeAddress,
    keyFromPath,
    schnorrkelKeypairFromSeed,
    mnemonicToMiniSecret
} from '@polkadot/util-crypto';

export const kusamaNode = 'wss://kusama-rpc.polkadot.io/';

// Trade variables
export const sellerHexSeed = process.env.SELLER_HEX_SEED;
export const adminHexSeed = process.env.ADMIN_HEX_SEED;
export const buyerHexSeed = process.env.BUYER_HEX_SEED;

export async function deriveAddress(hexSeed) {
  await cryptoWaitReady();
  const { publicKey } = keyFromPath(
    schnorrkelKeypairFromSeed(
      Buffer.from(hexSeed, 'hex')),
    [],
    'sr25519');
  return encodeAddress(publicKey, 2)
}

async function deriveEscrowAddress(addresses) {

}

export const buyerAddress = 'CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo';
export const adminAddress = 'HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2';
export const sellerAddress = 'J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc';
export const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';
export const tradeValue = 10000000000;
