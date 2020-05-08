/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
const { cryptoWaitReady } = require('@polkadot/util-crypto');
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');
const { Timepoint } = require('@polkadot/types/interfaces');

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


async function asMulti (signerHexSeed, otherSignatories) {
    const api = await ApiPromise.create({ provider: wsProvider });

    await cryptoWaitReady();
    const keyring = new Keyring({ type: 'sr25519' });
    
    const signersKey = keyring.addFromSeed(
      Buffer.from(signerHexSeed, 'hex'));

    const baseTransfer = api.tx.balances.transfer(buyerAddress, tradeValue)
    const initialCall = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, baseTransfer);
    const tx = api.tx.utility.asMulti(threshold, otherSignatories, timepoint, initialCall);
  
    const promise = new Promise((resolve, reject) => {
      tx.signAndSend(signersKey, ({ events = [], status }) => {
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


async function releaseEscrow (signerHexSeed, otherSignatories, destAddress, timePoint) {
  const api = await ApiPromise.create({ provider: wsProvider });

  await cryptoWaitReady();
  const keyring = new Keyring({ type: 'sr25519' });
  
  const signersKey = keyring.addFromSeed(
    Buffer.from(signerHexSeed, 'hex'));
  
  const baseTransfer = api.tx.balances.transfer(destAddress, tradeValue);

  const tx = api.tx.utility.asMulti(threshold, otherSignatories, timePoint, baseTransfer);

  const hash = await tx.signAndSend(signersKey);

  console.log('Release escrow transfer sent with hash', hash.toHex());
}
  
async function standardTrade () {
  //const hash = await fundEscrow();
  //console.log(`event hash ${hash}`);

  const timePoint = await asMulti(
    sellerHexSeed,
    [buyerAddress, adminAddress]
  );

  console.log('Timepoint', timePoint);

  //releaseEscrow(
  //  adminHexSeed,
  //  [buyerAddress, sellerAddress],
  //  buyerAddress,
  //  {
  //    height: 2210077,
  //    index: 3
  //  },
  //).catch(console.error);
}

standardTrade();
