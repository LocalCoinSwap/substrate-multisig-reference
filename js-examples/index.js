/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
import { cryptoWaitReady } from '@polkadot/util-crypto';
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');
import { SubmittableExtrinsic } from '@polkadot/api/promise/types';

// Instantiate the API
const wsProvider = new WsProvider('wss://kusama-rpc.polkadot.io/');

// const buyerKey = keyring.addFromSeed(
//     Buffer.from('64c29cbfc0cec793d1c62a5d80261aa8a1c03535379cedbb0601c1f89ad2271e', 'hex'));
// const adminKey = keyring.addFromSeed(
//     Buffer.from('2cf02efa64eb4ba75fa2f42f69dcf5548e821f1e852e2b26aa1b09d5eda0065a', 'hex'));
const sellerHexSeed = '8b3585743475df08238ff09c401ff8639171c9ad2584045f4b23a5e4f5e326f8';
const buyerAddress = 'CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo';
const adminAddress = 'HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2';

async function fundEscrow () {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const sellerKey = keyring.addFromSeed(
    Buffer.from(sellerHexSeed, 'hex'));

  const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';
  const transfer = api.tx.balances.transfer(escrowAddress, 100000000000);

  // Sign and send the transaction using our account
  const hash = await transfer.signAndSend(sellerKey);

  console.log('Transfer sent with hash', hash.toHex());
}

async function asMulti () {
    const api = await ApiPromise.create({ provider: wsProvider });

    await cryptoWaitReady();
    const keyring = new Keyring({ type: 'sr25519' });
    
    const sellerKey = keyring.addFromSeed(
      Buffer.from(sellerHexSeed, 'hex'));

    // Variables for asMulti
    let threshold = 2;
    let others = [
      buyerAddress,
      adminAddress];
    let timepoint = null;

    const baseTransfer = api.tx.balances.transfer(buyerAddress, 90000000000)
    const initialCall = api.tx.utility.asMulti(threshold, others, timepoint, baseTransfer);
    const tx = api.tx.utility.asMulti(threshold, others, timepoint, initialCall);
  
    const hash = await tx.signAndSend(sellerKey);
  
    console.log('Transfer sent with hash', hash.toHex());
  }
  

//fundEscrow().catch(console.error).finally(() => process.exit());
asMulti().catch(console.error).finally(() => process.exit());
