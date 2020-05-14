import { deriveAddress } from '../ksmref/utils';

test('Ensure address from hex seed works', async () => {
  const consoleLog = console.log;
  console.log = jest.fn();

  const testAddress = "ELcHqGzZ1Sz5KFo5NNSGrRKzR3LpTtM3BJ6emUMt4hxLj48";

  // This mnemonic is not used, it is okay to keep it like this in test
  // Generated from mnemonic = "giant name bulk smooth coconut gather urban cattle anchor habit hip mad"
  const seed = "bfd31b550f01a06120b7d21833f5705da3c8b90fda468fd562a9a32c03fe187c";

  const derivedAddress = await deriveAddress(seed);
  console.debug(derivedAddress, "------------------------");

  expect(derivedAddress).toBe(testAddress);
  console.log = consoleLog;
});
