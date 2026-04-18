'use client';

import { CreditCard } from 'lucide-react';
import { PaymentMethodCard } from './PaymentMethodCard';
import { PaymentIcons } from './PaymentIcons';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';

interface CardPaymentOptionProps {
  isSelected: boolean;
  onSelect: (method: PaymentMethodType) => void;
}

export const CardPaymentOption = ({ isSelected, onSelect }: CardPaymentOptionProps) => {
  return (
    <PaymentMethodCard
      icon={CreditCard}
      name="Credit / Debit Card"
      description="Pay directly with your card"
      isSelected={isSelected}
      onClick={() => onSelect('card')}
    >
      <div className="space-y-3">
        <p className="text-sm text-gray-600">Card payment integration coming soon.</p>
        <div className="flex items-center gap-2">
          <span className="text-xs text-gray-500">Supported:</span>
          <PaymentIcons />
        </div>
      </div>
    </PaymentMethodCard>
  );
};
