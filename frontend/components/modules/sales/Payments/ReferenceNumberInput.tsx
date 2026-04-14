'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';

const HINTS: Record<string, string> = {
  CASH: 'Receipt number',
  BANK_TRANSFER: 'Transaction ID',
  CREDIT_CARD: 'Last 4 digits of card',
  DEBIT_CARD: 'Last 4 digits of card',
  CHEQUE: 'Cheque number',
  ONLINE: 'Transaction reference',
};

interface ReferenceNumberInputProps {
  value?: string;
  onChange: (value: string) => void;
  paymentMethod?: string;
  error?: string;
}

export function ReferenceNumberInput({
  value,
  onChange,
  paymentMethod,
  error,
}: ReferenceNumberInputProps) {
  const hint = paymentMethod ? (HINTS[paymentMethod] ?? 'Reference number') : 'Reference number';

  return (
    <div className="space-y-1.5">
      <Label>Reference Number</Label>
      <Input
        value={value ?? ''}
        onChange={(e) => onChange(e.target.value)}
        placeholder={hint}
        maxLength={100}
        className={error ? 'border-red-500' : ''}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
