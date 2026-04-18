'use client';

import { CreditCard, Banknote, Building2, Smartphone } from 'lucide-react';
import { useStoreCheckoutStore } from '@/stores/store';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';

const methodConfig: Record<PaymentMethodType, { label: string; icon: typeof CreditCard }> = {
  payhere: { label: 'PayHere', icon: CreditCard },
  card: { label: 'Credit / Debit Card', icon: CreditCard },
  bank_transfer: { label: 'Bank Transfer', icon: Building2 },
  cod: { label: 'Cash on Delivery', icon: Banknote },
  koko: { label: 'KOKO – Buy Now Pay Later', icon: Smartphone },
  mintpay: { label: 'MintPay – Installments', icon: Smartphone },
};

export const PaymentSummary = () => {
  const paymentMethod = useStoreCheckoutStore((s) => s.paymentMethod);
  const paymentDetails = useStoreCheckoutStore((s) => s.paymentDetails);

  if (!paymentMethod) {
    return <p className="text-sm text-gray-500">No payment method selected.</p>;
  }

  const config = methodConfig[paymentMethod];
  const Icon = config.icon;

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-3 text-sm">
        <Icon className="h-4 w-4 shrink-0 text-gray-400" />
        <span className="text-gray-900">{config.label}</span>
      </div>

      {paymentMethod === 'cod' && (
        <p className="text-sm text-amber-600 ml-7">COD fee: ₨200 will be added to your total.</p>
      )}

      {paymentMethod === 'bank_transfer' && paymentDetails?.transactionId && (
        <p className="text-sm text-gray-500 ml-7">Transaction ID: {paymentDetails.transactionId}</p>
      )}
    </div>
  );
};
