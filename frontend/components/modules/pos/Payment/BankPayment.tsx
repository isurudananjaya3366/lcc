'use client';

import { Button } from '@/components/ui/button';

interface BankPaymentProps {
  amount: number;
  reference: string;
  onReferenceChange: (value: string) => void;
  onSubmit: (reference: string) => void;
}

export function BankPayment({ amount, reference, onReferenceChange, onSubmit }: BankPaymentProps) {
  return (
    <div className="space-y-3">
      <div className="rounded-md border border-gray-200 px-3 py-2 dark:border-gray-700">
        <p className="text-xs text-gray-500">Bank Transfer Amount</p>
        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
          ₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </p>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
          Transfer Reference No.
        </label>
        <input
          type="text"
          value={reference}
          onChange={(e) => onReferenceChange(e.target.value)}
          placeholder="e.g. TXN-20240101-001"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
        />
      </div>

      <Button
        className="w-full"
        size="lg"
        onClick={() => onSubmit(reference)}
        disabled={!reference.trim()}
      >
        Confirm Bank Transfer
      </Button>
    </div>
  );
}
