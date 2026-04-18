'use client';

import { Building2 } from 'lucide-react';
import { PaymentMethodCard } from './PaymentMethodCard';
import { BankDetailsDisplay } from './BankDetailsDisplay';
import { ReceiptUpload } from './ReceiptUpload';
import type { PaymentMethodType } from '@/types/storefront/checkout.types';

interface BankTransferOptionProps {
  isSelected: boolean;
  onSelect: (method: PaymentMethodType) => void;
}

export const BankTransferOption = ({ isSelected, onSelect }: BankTransferOptionProps) => {
  return (
    <PaymentMethodCard
      icon={Building2}
      name="Bank Transfer"
      description="Transfer to our bank account"
      isSelected={isSelected}
      onClick={() => onSelect('bank_transfer')}
    >
      <div className="space-y-4">
        <BankDetailsDisplay />
        <ReceiptUpload />
      </div>
    </PaymentMethodCard>
  );
};
