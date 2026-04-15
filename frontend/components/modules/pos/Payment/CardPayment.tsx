'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface CardPaymentProps {
  amount: number;
  reference: string;
  onReferenceChange: (value: string) => void;
  onSubmit: (reference: string) => void;
}

export function CardPayment({ amount, reference, onReferenceChange, onSubmit }: CardPaymentProps) {
  const [lastFour, setLastFour] = useState('');

  return (
    <div className="space-y-3">
      <div className="rounded-md border border-gray-200 px-3 py-2 dark:border-gray-700">
        <p className="text-xs text-gray-500">Card Payment Amount</p>
        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
          ₨ {amount.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </p>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
          Authorization / Reference No.
        </label>
        <input
          type="text"
          value={reference}
          onChange={(e) => onReferenceChange(e.target.value)}
          placeholder="e.g. AUTH-12345"
          className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700 dark:text-gray-300">
          Last 4 Digits (optional)
        </label>
        <input
          type="text"
          value={lastFour}
          onChange={(e) => setLastFour(e.target.value.replace(/\D/g, '').slice(0, 4))}
          placeholder="XXXX"
          maxLength={4}
          className="w-24 rounded-md border border-gray-300 px-3 py-2 text-sm dark:border-gray-600 dark:bg-gray-800"
        />
      </div>

      <Button
        className="w-full"
        size="lg"
        onClick={() => onSubmit(reference)}
        disabled={!reference.trim()}
      >
        Confirm Card Payment
      </Button>
    </div>
  );
}
