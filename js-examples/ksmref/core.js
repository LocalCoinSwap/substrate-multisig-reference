const { cryptoWaitReady } = require('@polkadot/util-crypto');
const { ApiPromise } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');


import { deriveAddress } from './utils';
import {
  adminHexSeed,
  buyerHexSeed,
  sellerHexSeed,
  escrowAddress,
  threshold,
  tradeValue,
} from '../config';


export async function sellerFundEscrow (wsProvider) {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const sellerKey = keyring.addFromSeed(
    Buffer.from(sellerHexSeed, 'hex'));

  // Make an escrow funding transaction, waiting for inclusion
  const tx = api.tx.balances.transfer(escrowAddress, tradeValue)

  const promise = new Promise((resolve, reject) => {
    tx.signAndSend(sellerKey, ({ events = [], status }) => {
      console.debug(`Current transaction status is ${status.type}`)
      if (status.isFinalized) {
        console.debug(`Transaction was included at blockHash ${status.asFinalized}`);
        // Loop through Vec<EventRecord> to display all events
        events.forEach(({ phase, event: { data, method, section } }) => {
          console.debug(`\t' ${phase}: ${section}.${method}:: ${data}`);
        });

        resolve(status.asFinalized);
      }
    });
  });

  const hash = await promise;
  return hash;
}

export async function sellerApproveRelease (wsProvider, timepoint=null) {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const signersKey = keyring.addFromSeed(
    Buffer.from(sellerHexSeed, 'hex'));

  const buyerAddress = await deriveAddress(buyerHexSeed);
  const adminAddress = await deriveAddress(adminHexSeed);
  const otherSignatories = [buyerAddress, adminAddress].sort();

  const baseTransfer = api.tx.balances.transfer(buyerAddress, tradeValue);
  const tx = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, baseTransfer);

  const promise = new Promise((resolve, reject) => {
    tx.signAndSend(signersKey, ({ events = [], status }) => {
      console.debug(`Current transaction status is ${status.type}`)
      let index;
      let blockHash;
      if (status.isFinalized) {
        console.debug(`Transaction was included at blockHash ${status.asFinalized}`);
        blockHash = `${status.asFinalized}`;

        // Loop through Vec<EventRecord> to find the index from the multiSig creation
        events.forEach(({ phase, event: { data, method, section } }) => {
          console.debug(`\t' ${phase}: ${section}.${method}:: ${data}`);
          if (`${method}` === 'NewMultisig') {
            index = parseInt(phase._raw, 10);
          }
          console.debug('Transaction index', index);
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

export async function adminFinalizeRelease (wsProvider, timePoint) {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const signersKey = keyring.addFromSeed(
    Buffer.from(adminHexSeed, 'hex'));

  const buyerAddress = await deriveAddress(buyerHexSeed);
  const sellerAddress = await deriveAddress(sellerHexSeed);
  const otherSignatories = [buyerAddress, sellerAddress].sort();

  const baseTransfer = api.tx.balances.transfer(buyerAddress, tradeValue);
  const tx = api.tx.utility.asMulti(threshold, otherSignatories, timePoint, baseTransfer);

  const promise = new Promise((resolve, reject) => {
    tx.signAndSend(signersKey, ({ events = [], status }) => {
      console.debug(`Current transaction status is ${status.type}`)
      if (status.isFinalized) {
        console.debug(`Transaction was included at blockHash ${status.asFinalized}`);

        // Loop through Vec<EventRecord> to display all events
        events.forEach(({ phase, event: { data, method, section } }) => {
          console.debug(`\t' ${phase}: ${section}.${method}:: ${data}`);
        });

        resolve(`${status.asFinalized}`);
      }
    });
  });

  const hash = await promise;
  return hash;
}
