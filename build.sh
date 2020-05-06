#!/bin/sh

cd bindings/bip39 && cargo +nightly build --release
cd ../..
MODULE_NAME="bip39.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv bindings/bip39/target/release/libbip39.dylib ./bindings/$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv bindings/bip39/target/release/libbip39.so ./bindings/$MODULE_NAME
fi

cd bindings/sr25519 && cargo +nightly build --release
cd ../..
MODULE_NAME="sr25519.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv bindings/sr25519/target/release/libsr25519.dylib ./bindings/$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv bindings/sr25519/target/release/libsr25519.so ./bindings/$MODULE_NAME
fi

cd bindings/util-multisig && cargo +nightly build --release
cd ../..
MODULE_NAME="multisig.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv bindings/util-multisig/target/release/libmultisig.dylib ./bindings/$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv bindings/util-multisig/target/release/libmultisig.so ./bindings/$MODULE_NAME
fi
