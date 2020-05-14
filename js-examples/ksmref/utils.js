import {
  cryptoWaitReady,
  encodeAddress,
  keyFromPath,
  schnorrkelKeypairFromSeed,
} from '@polkadot/util-crypto';

export async function deriveAddress(hexSeed) {
  await cryptoWaitReady();
  const { publicKey } = keyFromPath(
    schnorrkelKeypairFromSeed(
      Buffer.from(hexSeed, 'hex')),
    [],
    'sr25519');
  return encodeAddress(publicKey, 2)
}
