import { WsProvider } from '@polkadot/api';

import {
  sellerFundEscrow,
  sellerApproveRelease,
  buyerApprovesRelease,
  adminFinalizeRelease,
  sellerApprovesCancel,
  adminFinalizeCancel,
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

export async function fundsBackToSellerByCancellation () {
  console.debug('============FUNDS BACK TO SELLER EXAMPLE============');
  const wsProvider = new WsProvider(kusamaNode);

  const hash = await sellerFundEscrow(wsProvider);
  console.debug('SELLER FUND ESCROW HASH:', hash);

  const timePoint = await sellerApprovesCancel(wsProvider);
  console.debug('SELLER APPROVE CANCEL TIMEPOINT: ', timePoint);

  const release = await adminFinalizeCancel(
    wsProvider,
    timePoint,
  );

  console.debug('ADMIN FINALIZES CANCEL HASH: ', release);
  return;
}

export async function disputeInFavorOfBuyer () {
  console.debug('============FUNDS RELEASED TO BUYER AFTER DISPUTE============');
  const wsProvider = new WsProvider(kusamaNode);

  const hash = await sellerFundEscrow(wsProvider);
  console.debug('SELLER FUND ESCROW HASH:', hash);

  const timePoint = await buyerApprovesRelease(wsProvider);
  console.debug('BUYER APPROVE RELEASE TIMEPOINT: ', timePoint);

  const release = await adminFinalizeRelease(
    wsProvider,
    timePoint,
  );

  console.debug('ADMIN FINALIZES RELEASE HASH: ', release);
  return;
}
