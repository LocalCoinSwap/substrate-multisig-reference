/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
const { cryptoWaitReady } = require('@polkadot/util-crypto');
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');

// Instantiate the API
const wsProvider = new WsProvider('wss://kusama-rpc.polkadot.io/');

// Trade variables
const sellerHexSeed = '8b3585743475df08238ff09c401ff8639171c9ad2584045f4b23a5e4f5e326f8';
const adminHexSeed = '2cf02efa64eb4ba75fa2f42f69dcf5548e821f1e852e2b26aa1b09d5eda0065a';
const buyerAddress = 'CdVuGwX71W4oRbXHsLuLQxNPns23rnSSiZwZPN4etWf6XYo';
const adminAddress = 'HvqnQxDQbi3LL2URh7WQfcmi8b2ZWfBhu7TEDmyyn5VK8e2';
const sellerAddress = 'J9aQobenjZjwWtU2MsnYdGomvcYbgauCnBeb8xGrcqznvJc';
const tradeValue = 25000000000;

// Additional variables for asMulti
let threshold = 2;
let timepoint = null;


async function sellerFundEscrow () {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });

  const sellerKey = keyring.addFromSeed(
    Buffer.from(sellerHexSeed, 'hex'));

  const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';

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


async function sellerApproveRelease (signerHexSeed, otherSignatories) {
    const api = await ApiPromise.create({ provider: wsProvider });

    await cryptoWaitReady();
    const keyring = new Keyring({ type: 'sr25519' });
    
    const signersKey = keyring.addFromSeed(
      Buffer.from(signerHexSeed, 'hex'));

    const baseTransfer = api.tx.balances.transfer(buyerAddress, tradeValue);
    const tx = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, baseTransfer);
  
    const promise = new Promise((resolve, reject) => {
      tx.signAndSend(signersKey, ({ events = [], status }) => {
        console.log(`Current transaction status is ${status.type}`)
        console.log(`Current transaction status is ${status}`)
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
  
async function standardTrade () {
  const hash = await sellerFundEscrow();
  console.log(`event hash ${hash}`);
 
  const timePoint = await sellerApproveRelease(
    sellerHexSeed,
    [buyerAddress, adminAddress]
  );
  console.log('timePoint', timePoint);

  const release = await adminFinalizeRelease(
    adminHexSeed,
    [buyerAddress, sellerAddress],
    buyerAddress,
    timePoint,
  );

  console.log('release', release);
}

standardTrade();
