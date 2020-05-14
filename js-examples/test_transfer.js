/* eslint-disable header/header */
/* eslint-disable @typescript-eslint/require-await */
/* eslint-disable @typescript-eslint/no-var-requires */

// Import the API & Provider and some utility functions
const { ApiPromise, WsProvider } = require('@polkadot/api');

const { Keyring } = require('@polkadot/keyring');

import {
  kusamaNode,
} from './config';

// Some constants we are using in this sample
const GOKU = 'HNYVqU52eCHnLVkJ7Npzqi4YuK5MPjzs78mJQTRP3k5dL8B';
const AMOUNT = 2000000000;


// Instantiate the API
const wsProvider = new WsProvider(kusamaNode);


async function main () {
  // Create the API and wait until ready
  const api = await ApiPromise.create({ provider: wsProvider });

  const keyring = new Keyring({ type: 'sr25519' });

  // Get the nonce for the admin key
  const { nonce } = await api.query.system.account(GOKU);

  // Find the actual keypair in the keyring

  const gokuKeyring = keyring.addFromMnemonic("green peasant afraid mushroom pretty cash axis outdoor gossip alert group hood");

  // Create a new random recipient
  const recipient = "GeyL1R2rPeCAaxNd9bztQAyNrDJ8PfFrxbhXQrXbbbEgmoU";

  console.debug('Sending', AMOUNT, 'from', gokuKeyring.address, 'to', recipient, 'with nonce', nonce.toString());

  // Do the transfer and track the actual status
  const tx = api.tx.balances.transfer(recipient, AMOUNT);
  console.debug(tx);
  tx.signAndSend(gokuKeyring, { nonce }, ({ events = [], status }) => {
      console.debug('Transaction status:', status.type);

      if (status.isInBlock) {
        console.debug('Included at block hash', status.asInBlock.toHex());
        console.debug('Events:');

        events.forEach(({ event: { data, method, section }, phase }) => {
          console.debug('\t', phase.toString(), `: ${section}.${method}`, data.toString());
        });
      } else if (status.isFinalized) {
        console.debug('Finalized block hash', status.asFinalized.toHex());

        process.exit(0);
      }
    });
}

main().catch(console.error);
