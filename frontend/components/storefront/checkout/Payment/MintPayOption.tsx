'use client';

import { Wallet } from 'lucide-react';
import { PaymentMethodCard } from './PaymentMethodCard';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';

const MINTPAY_MIN_ORDER = 2000;

interface MintPayOptionProps {
  isSelected: boolean;
  onSelect: (method: PaymentMethodType) => void;
  orderTotal?: number;
}

export const MintPayOption = ({ isSelected, onSelect, orderTotal = 0 }: MintPayOptionProps) => {
  const installment = orderTotal > 0 ? Math.ceil(orderTotal / 3) : 0;
  const meetsMinimum = orderTotal >= MINTPAY_MIN_ORDER;

  return (
    <PaymentMethodCard
      icon={Wallet}
      name="MintPay"
      description="3 easy installments"
      badge="BNPL"
      badgeColor="bg-teal-100 text-teal-700"
      isSelected={isSelected}
      onClick={() => onSelect('mintpay')}
    >
      <div className="space-y-3">
        {orderTotal > 0 && (
          <div className="rounded-lg border border-gray-200 p-3 space-y-1.5">
            <p className="text-xs font-medium text-gray-600">Installment Breakdown</p>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">3 monthly payments of</span>
              <span className="font-medium text-gray-900">₨{installment.toLocaleString()}/mo</span>
            </div>
            <p className="text-[10px] text-gray-400">Split your payment into 3</p>
          </div>
        )}

        {!meetsMinimum && orderTotal > 0 && (
          <div className="rounded bg-amber-50 border border-amber-200 p-2">
            <p className="text-xs text-amber-800">
              Minimum order of ₨{MINTPAY_MIN_ORDER.toLocaleString()} required for MintPay.
            </p>
          </div>
        )}

        {(orderTotal === 0 || meetsMinimum) && (
          <p className="text-xs text-gray-500">Min order: ₨{MINTPAY_MIN_ORDER.toLocaleString()}</p>
        )}
      </div>
    </PaymentMethodCard>
  );
};
