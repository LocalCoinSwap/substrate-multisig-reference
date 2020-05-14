/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
const { cryptoWaitReady } = require('@polkadot/util-crypto');
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');


import {
  createSigningPayload,
  getRegistry,
  methods,
  createSignedTx,
} from '@substrate/txwrapper';

import {
  kusamaNode,
  sellerHexSeed,
  adminHexSeed,
  buyerHexSeed,
  deriveAddress,
  // deriveEscrowAddress,
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

  const sellerAddress = await deriveAddress(sellerHexSeed)

  // Get generic blockchain and account data
  const { number, hash} = await api.rpc.chain.getHeader();
  const genesisHash = await api.rpc.chain.getBlockHash([0]);
  const { specVersion } = await api.rpc.state.getRuntimeVersion();
  const { nonce } = await api.query.system.account(sellerAddress);

  // Parse generic data into JSON value format
  const latestBlockNumber = parseInt(number._raw, 10);
  const latestBlockHash = hash.toString('hex');
  const genesisBlockHash = genesisHash.toString('hex');
  const spec = parseInt(specVersion, 10);

  // Returns huge away of data about the blockchain
  const metadataRpc = await api.rpc.state.getMetadata();

  // Appears to give an object with functions relevant to the chain
  const registry = getRegistry('Kusama', 'kusama', spec);

  // Unsigned JSON
  const unsigned = methods.balances.transfer(
    {
      value: tradeValue,
      dest: escrowAddress,
    },
    {
      address: sellerAddress,
      blockHash: latestBlockHash,
      blockNumber: latestBlockNumber,
      eraPeriod: 64,  // Kusama specific variable
      genesisHash: genesisBlockHash,
      metadataRpc,
      nonce,
      specVersion: spec,
      tip: 0,
    },
    {
      metadata: metadataRpc,
      registry,
    }
  );

  // Construct the signing payload from an unsigned transaction.
  const signingPayload = registry.createType('ExtrinsicPayload', unsigned, { version: unsigned.version }).toHex();
  console.debug(`\nB: Payload to Sign: ${signingPayload}`);

  // Sign a payload. This operation should be performed on an offline device.
  const { signature } = registry.createType('ExtrinsicPayload', signingPayload, { version: 4 }).sign(sellerKey);
  console.debug(`\nSignature: ${signature}`);

  // Serialize a signed transaction.
  const tx = createSignedTx(unsigned, signature, { registry });
  console.debug(`\nTransaction to Submit: ${tx}`);

  const promise = new Promise((resolve, reject) => {
    api.rpc.author.submitExtrinsic(tx, (x) => {
      console.debug(`Blockchain tx hash for submitted transaction: ${x}`)
      resolve(x);
    });
  });

  const submittedHash = await promise;
  return submittedHash;
}


async function approveAsMulti (signerHexSeed, otherSignatories, baseTransferAddress) {
    const api = await ApiPromise.create({ provider: wsProvider });

    await cryptoWaitReady();
    const keyring = new Keyring({ type: 'sr25519' });

    const signersKey = keyring.addFromSeed(
      Buffer.from(signerHexSeed, 'hex'));

    const baseTransfer = api.tx.balances.transfer(baseTransferAddress, tradeValue);
    const tx = api.tx.utility.approveAsMulti(threshold, otherSignatories, timepoint, baseTransfer.method.hash);

    // const promise = new Promise((resolve, reject) => {
    //   tx.signAndSend(signersKey, ({ events = [], status }) => {
    //     console.debug(`Current transaction status is ${status.type}`)
    //     let index;
    //     let blockHash;
    //     if (status.isFinalized) {
    //       console.debug(`Transaction was included at blockHash ${status.asFinalized}`);
    //       blockHash = `${status.asFinalized}`;

    //       // Loop through Vec<EventRecord> to find the index from the multiSig creation
    //       events.forEach(({ phase, event: { data, method, section } }) => {
    //         console.debug(`\t' ${phase}: ${section}.${method}:: ${data}`);
    //         if (`${method}` === 'NewMultisig') {
    //           index = parseInt(phase._raw, 10);
    //         }
    //         console.debug('Transaction index', index);
    //       });

    //       resolve({ index, blockHash });
    //     }
    //   });
    // });

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

// TODO: Automate ordering of signatories to prevent production errors
async function standardTrade () {
  const buyerAddress = await deriveAddress(buyerHexSeed);
  const sellerAddress = await deriveAddress(sellerHexSeed);
  const adminAddress = await deriveAddress(adminHexSeed);

  console.debug('approveAsMulti example');

  // const hash = await sellerFundEscrow();
  // console.debug(`event hash ${hash}`);

  const timePoint = await approveAsMulti(
    sellerHexSeed,
    [adminAddress, buyerAddress],
    buyerAddress,
  );
  console.debug('timePoint', timePoint);

  //const release = await adminFinalizeRelease(
  //  adminHexSeed,
  //  [buyerAddress, sellerAddress],
  //  buyerAddress,
  //  timePoint,
  //);

  console.debug('release', release);
  process.exit();
}

standardTrade();
