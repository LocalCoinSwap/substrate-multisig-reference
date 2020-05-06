import { cryptoWaitReady } from '@polkadot/util-crypto';
import {
    encodeAddress,
    keyFromPath,
    schnorrkelKeypairFromSeed,
    mnemonicToMiniSecret
 } from '@polkadot/util-crypto';
const mnemonic = "prefer fashion insect dizzy energy marble forget artefact aspect short surface leave";
const seed = mnemonicToMiniSecret(mnemonic, undefined);

function bufferToHex (buffer) {
    return [...new Uint8Array (buffer)]
        .map (b => b.toString (16).padStart (2, "0"))
        .join ("");
}

async function main () {
    await cryptoWaitReady();
    console.log('[SEED]', bufferToHex(seed));
    const { publicKey, secretKey } = keyFromPath(schnorrkelKeypairFromSeed(seed), [], 'sr25519');
    console.log('[PUBLIC KEY]', bufferToHex(publicKey));
    console.log('[ADDRESS]', encodeAddress(publicKey, 2));
}
main()

/*
OUTPUT
 [SEED] 3f686928bda5b57a0992c999aea74d65f844be234686871a2ddc6b003d586786
 [PUBLIC KEY] 8852f77f2aea5d2d5808cefa7cd49a3ed0ce1f1aa8ff2564c3cb96cb2510337d
 [ADDRESS] Ff4gBd7WcHgsNVhr5HGPQXQx4PzPHGtHdNVaCRK5d5KeMHh
*/
