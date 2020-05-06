#!/bin/sh

cd bip39 && cargo +nightly build --release
cd ..
MODULE_NAME="bip39.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv bip39/target/release/libbip39.dylib ./$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv bip39/target/release/libbip39.so ./$MODULE_NAME
fi

cd sr25519 && cargo +nightly build --release
cd ..
MODULE_NAME="sr25519.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv sr25519/target/release/libsr25519.dylib ./$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv sr25519/target/release/libsr25519.so ./$MODULE_NAME
fi
