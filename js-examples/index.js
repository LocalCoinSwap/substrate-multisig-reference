/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
import { cryptoWaitReady } from '@polkadot/util-crypto';
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');
import { Timepoint } from '@polkadot/types/interfaces';

// Instantiate the API
const wsProvider = new WsProvider('wss://kusama-rpc.polkadot.io/');

// Trade variables
const sellerHexSeed = '8b3585743475df08238ff09c401ff8639171c9ad2584045f4b23a5e4f5e326f8';
const adminHexSeed = '2cf02efa64eb4ba75fa2f42f69dcf5548e821f1e852e2b26aa1b09d5eda0065a';
const buyerHexSeed = '64c29cbfc0cec793d1c62a5d80261aa8a1c03535379cedbb0601c1f89ad2271e';
const buyerAddress = 'CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo';
const adminAddress = 'HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2';
const sellerAddress = 'J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc';
const tradeValue = 100000000000;

// Additional variables for asMulti
let threshold = 2;
let timepoint = null;


async function fundEscrow () {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const sellerKey = keyring.addFromSeed(
    Buffer.from(sellerHexSeed, 'hex'));

  const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';
  const transfer = api.tx.balances.transfer(escrowAddress, tradeValue);

  // Sign and send the transaction using our account
  const hash = await transfer.signAndSend(sellerKey);

  console.log('Fund escrow transfer sent with hash', hash.toHex());
}


async function asMulti (signerHexSeed, otherSignatories, message) {
    const api = await ApiPromise.create({ provider: wsProvider });

    await cryptoWaitReady();
    const keyring = new Keyring({ type: 'sr25519' });
    
    const signersKey = keyring.addFromSeed(
      Buffer.from(signerHexSeed, 'hex'));

    const baseTransfer = api.tx.balances.transfer(buyerAddress, tradeValue)
    const initialCall = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, baseTransfer);
    const tx = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, initialCall);
  
    const hash = await tx.signAndSend(signersKey);
  
    console.log(message, hash.toHex());
}


async function releaseEscrow (signerHexSeed, otherSignatories) {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });
  
  const signersKey = keyring.addFromSeed(
    Buffer.from(signerHexSeed, 'hex'));
  
  const baseTransfer = api.tx.balances.transfer(buyerAddress, tradeValue);

  /*
  * NOTE: This is from the docs, there is some tomfoolery required with timepoint
  *
  * - `maybe_timepoint`: If this is the first approval, then this must be `None`. If it is
  * not the first approval, then it must be `Some`, with the timepoint (block number and
  * transaction index) of the first approval transaction.
  */
  
  // const info = await api.query.utility.multisigs(buyerAddress, baseTransfer.hash);
  // console.log('info', info, baseTransfer.hash);
  // timepoint = info.unwrap().when;

  const tx = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, baseTransfer);

  const hash = await tx.signAndSend(signersKey);

  console.log('Release escrow transfer sent with hash', hash.toHex());
}
  
async function standardTrade () {
  fundEscrow().catch(console.error);

  await new Promise(resolve => setTimeout(resolve, 10000));

  asMulti(
    sellerHexSeed,
    [buyerAddress, adminAddress],
    'AsMulti seller transaction'
  ).catch(console.error);

  await new Promise(resolve => setTimeout(resolve, 10000));

  asMulti(
    adminHexSeed,
    [buyerAddress, sellerAddress],
    'AsMulti admin transaction'
  ).catch(console.error);

  await new Promise(resolve => setTimeout(resolve, 10000));

  releaseEscrow(
    buyerHexSeed,
    [adminAddress, sellerAddress]
  ).catch(console.error);
}

standardTrade();
