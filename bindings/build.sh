#!/bin/sh

cargo +nightly build --release
MODULE_NAME="wasm_crypto.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv target/release/libwasm_crypto.dylib ./$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv target/release/libwasm_crypto.so ./$MODULE_NAME
fi
