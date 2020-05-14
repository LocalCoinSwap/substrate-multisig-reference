import { jest } from '@jest/globals';

import { fundsBackToSellerByCancellation } from '../ksmref/index';

jest.setTimeout(1000000); // 1000 secs

test('Cancellation and funds back to seller end-to-end trade', async () => {
  // Because it prints node_modules console.debugs too
  // and that shit is annoying, freezes the terminal
  const consoleLog = console.log;
  console.log = jest.fn();

  await fundsBackToSellerByCancellation();

  // Reset console log
  console.log = consoleLog;
});
