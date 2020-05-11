/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
const { cryptoWaitReady } = require('@polkadot/util-crypto');
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');

import {
  kusamaNode,
  sellerHexSeed,
  adminHexSeed,
  buyerHexSeed,
  deriveAddress,
  deriveEscrowAddress,
  tradeValue,
} from './config';

// Instantiate the API
const wsProvider = new WsProvider(kusamaNode);

// Default values
let threshold = 2;
let timepoint = null;

const escrowAddress = 'HmGLJ6sG34vyBwyQSJWvN8HUByatcisuoyuyDXS4JeUZScm';

async function sellerFundEscrow () {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const sellerKey = keyring.addFromSeed(
    Buffer.from(sellerHexSeed, 'hex'));

  // Make an escrow funding transaction, waiting for inclusion
  const tx = api.tx.balances.transfer(escrowAddress, tradeValue)

  const promise = new Promise((resolve, reject) => {
    tx.signAndSend(sellerKey, ({ events = [], status }) => {
      console.log(`Current transaction status is ${status.type}`)
      if (status.isFinalized) {
        console.log(`Transaction was included at blockHash ${status.asFinalized}`);
        // Loop through Vec<EventRecord> to display all events
        events.forEach(({ phase, event: { data, method, section } }) => {
          console.log(`\t' ${phase}: ${section}.${method}:: ${data}`);
        });

        resolve(status.asFinalized);
      }
    });
  });

  const hash = await promise;
  return hash;
}


async function approveAsMulti (signerHexSeed, otherSignatories, baseTransferAddress) {
    const api = await ApiPromise.create({ provider: wsProvider });

    await cryptoWaitReady();
    const keyring = new Keyring({ type: 'sr25519' });

    const signersKey = keyring.addFromSeed(
      Buffer.from(signerHexSeed, 'hex'));

    const baseTransfer = api.tx.balances.transfer(baseTransferAddress, tradeValue);
    const tx = api.tx.utility.approveAsMulti(threshold, otherSignatories, timepoint, baseTransfer.method.hash);

    const promise = new Promise((resolve, reject) => {
      tx.signAndSend(signersKey, ({ events = [], status }) => {
        console.log(`Current transaction status is ${status.type}`)
        let index;
        let blockHash;
        if (status.isFinalized) {
          console.log(`Transaction was included at blockHash ${status.asFinalized}`);
          blockHash = `${status.asFinalized}`;

          // Loop through Vec<EventRecord> to find the index from the multiSig creation
          events.forEach(({ phase, event: { data, method, section } }) => {
            console.log(`\t' ${phase}: ${section}.${method}:: ${data}`);
            if (`${method}` === 'NewMultisig') {
              index = parseInt(phase._raw, 10);
            }
            console.log('Transaction index', index);
          });

          resolve({ index, blockHash });
        }
      });
    });

    const { index, blockHash } = await promise;
    const signedBlock = await api.rpc.chain.getBlock(blockHash);
    const height = parseInt(signedBlock.block.header.number, 10)
    return { height, index };
}


async function adminFinalizeRelease (signerHexSeed, otherSignatories, destAddress, timePoint) {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const signersKey = keyring.addFromSeed(
    Buffer.from(signerHexSeed, 'hex'));

  const baseTransfer = api.tx.balances.transfer(destAddress, tradeValue);
  const tx = api.tx.utility.asMulti(threshold, otherSignatories, timePoint, baseTransfer);

  const promise = new Promise((resolve, reject) => {
    tx.signAndSend(signersKey, ({ events = [], status }) => {
      console.log(`Current transaction status is ${status.type}`)
      if (status.isFinalized) {
        console.log(`Transaction was included at blockHash ${status.asFinalized}`);

        // Loop through Vec<EventRecord> to display all events
        events.forEach(({ phase, event: { data, method, section } }) => {
          console.log(`\t' ${phase}: ${section}.${method}:: ${data}`);
        });

        resolve(`${status.asFinalized}`);
      }
    });
  });

  const hash = await promise;
  return hash;
}
// TODO: Automate ordering of signatories to prevent production errors
// TODO: What to do on failure
// TODO: Handling batching
async function standardTrade () {
  const buyerAddress = await deriveAddress(buyerHexSeed);
  const sellerAddress = await deriveAddress(sellerHexSeed);
  const adminAddress = await deriveAddress(adminHexSeed);

  console.log('approveAsMulti example');

  const hash = await sellerFundEscrow();
  console.log(`event hash ${hash}`);

  const timePoint = await approveAsMulti(
    sellerHexSeed,
    [adminAddress, buyerAddress],
    buyerAddress,
  );
  console.log('timePoint', timePoint);

  const release = await adminFinalizeRelease(
    adminHexSeed,
    [buyerAddress, sellerAddress],
    buyerAddress,
    timePoint,
  );

  console.log('release', release);
  process.exit();
}

standardTrade();
