'use client';

import { useStoreCheckoutStore } from '@/stores/store';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';
import { PayHereOption } from './PayHereOption';
import { CardPaymentOption } from './CardPaymentOption';
import { BankTransferOption } from './BankTransferOption';
import { CODOption } from './CODOption';
import { KOKOOption } from './KOKOOption';
import { MintPayOption } from './MintPayOption';

export const PaymentMethods = () => {
  const paymentMethod = useStoreCheckoutStore((s) => s.paymentMethod);
  const setPaymentMethod = useStoreCheckoutStore((s) => s.setPaymentMethod);

  const handleSelect = (method: PaymentMethodType) => {
    setPaymentMethod(method);
  };

  return (
    <div className="space-y-3">
      <PayHereOption isSelected={paymentMethod === 'payhere'} onSelect={handleSelect} />
      <CardPaymentOption isSelected={paymentMethod === 'card'} onSelect={handleSelect} />
      <BankTransferOption isSelected={paymentMethod === 'bank_transfer'} onSelect={handleSelect} />
      <CODOption isSelected={paymentMethod === 'cod'} onSelect={handleSelect} />
      <KOKOOption isSelected={paymentMethod === 'koko'} onSelect={handleSelect} />
      <MintPayOption isSelected={paymentMethod === 'mintpay'} onSelect={handleSelect} />
    </div>
  );
};
