#!/bin/sh

cd bindings/util-multisig && cargo +nightly build --release
cd ../..
MODULE_NAME="multisig.so"

if [[ "$OSTYPE" == "darwin"* ]]; then
  mv bindings/util-multisig/target/release/libmultisig.dylib ./bindings/$MODULE_NAME
else [[ "$OSTYPE" == "linux-gnu"* ]];
  mv bindings/util-multisig/target/release/libmultisig.so ./bindings/$MODULE_NAME
fi

pytest -v -s
