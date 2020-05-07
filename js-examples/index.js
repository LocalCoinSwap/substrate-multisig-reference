/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/unbound-method */

// Import the API, Keyring and some utility functions
const { ApiPromise, WsProvider } = require('@polkadot/api');
const { Keyring } = require('@polkadot/keyring');

// Instantiate the API
const wsProvider = new WsProvider('wss://kusama-rpc.polkadot.io/');
const api = await ApiPromise.create({ provider: wsProvider });

// Constuct the keying after the API (crypto has an async init)
const keyring = new Keyring({ type: 'sr25519' });

const sellerKey = keyring.addFromSeed(
  Buffer.from('8b3585743475df08238ff09c401ff8639171c9ad2584045f4b23a5e4f5e326f8', 'hex'));
const buyerKey = keyring.addFromSeed(
    Buffer.from('64c29cbfc0cec793d1c62a5d80261aa8a1c03535379cedbb0601c1f89ad2271e', 'hex'));
const adminKey = keyring.addFromSeed(
    Buffer.from('2cf02efa64eb4ba75fa2f42f69dcf5548e821f1e852e2b26aa1b09d5eda0065a', 'hex'));

async function fundEscrow () {
  const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';
  const transfer = api.tx.balances.transfer(escrowAddress, 100000000000);

  // Sign and send the transaction using our account
  const hash = await transfer.signAndSend(sellerKey);

  console.log('Transfer sent with hash', hash.toHex());
}

// IN PROGRESS
async function asMulti () {
    const escrowAddress = 'HFXXfXavDuKhLLBhFQTat2aaRQ5CMMw9mwswHzWi76m6iLt';
    const tx = api.tx.utility.asMulti(
        );
  
    // Sign and send the transaction using our account
    const hash = await tx.signAndSend(seller);
  
    console.log('Transfer sent with hash', hash.toHex());
  }
  

fundEscrow().catch(console.error).finally(() => process.exit());
