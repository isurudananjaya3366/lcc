'use client';

import { CreditCard } from 'lucide-react';
import { PaymentMethodCard } from './PaymentMethodCard';
import { PaymentIcons } from './PaymentIcons';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';

interface PayHereOptionProps {
  isSelected: boolean;
  onSelect: (method: PaymentMethodType) => void;
}

export const PayHereOption = ({ isSelected, onSelect }: PayHereOptionProps) => {
  return (
    <PaymentMethodCard
      icon={CreditCard}
      name="Pay via PayHere"
      description="Visa, Mastercard, Lanka QR, mobile wallets"
      isSelected={isSelected}
      onClick={() => onSelect('payhere')}
    >
      <div className="space-y-3">
        <p className="text-sm text-gray-600">
          You will be redirected to PayHere to complete payment.
        </p>
        <PaymentIcons />
      </div>
    </PaymentMethodCard>
  );
};
