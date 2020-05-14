import { WsProvider } from '@polkadot/api';

import {
  sellerFundEscrow,
  sellerApproveRelease,
  adminFinalizeRelease,
} from './core';

import {
  kusamaNode,
} from '../config';


export async function standardTrade () {
  console.debug('============STANDARD TRADE EXAMPLE============');
  const wsProvider = new WsProvider(kusamaNode);

  const hash = await sellerFundEscrow(wsProvider);
  console.debug('SELLER FUND ESCROW HASH:', hash);

  const timePoint = await sellerApproveRelease(wsProvider);
  console.debug('SELLER APPROVE RELEASE TIMEPOINT: ', timePoint);

  const release = await adminFinalizeRelease(
    wsProvider,
    timePoint,
  );

  console.debug('ADMIN FINALIZES RELEASE HASH: ', release);
  return;
}
