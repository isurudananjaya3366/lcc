'use client';

import { Numpad } from './Numpad';
import { QuickAmounts } from './QuickAmounts';
import { ChangeCalculator } from './ChangeCalculator';
import { Button } from '@/components/ui/button';

interface CashPaymentProps {
  amount: number;
  cashTendered: number;
  onCashChange: (value: number) => void;
  onSubmit: (amount: number) => void;
}

export function CashPayment({ amount, cashTendered, onCashChange, onSubmit }: CashPaymentProps) {
  const changeDue = Math.max(0, cashTendered - amount);
  const canSubmit = cashTendered >= amount;

  return (
    <div className="space-y-3">
      {/* Cash Tendered Display */}
      <div className="rounded-md border border-gray-200 px-3 py-2 dark:border-gray-700">
        <p className="text-xs text-gray-500">Cash Tendered</p>
        <p className="text-xl font-bold text-gray-900 dark:text-gray-100">
          ₨ {cashTendered.toLocaleString('en-LK', { minimumFractionDigits: 2 })}
        </p>
      </div>

      {/* Quick Amounts */}
      <QuickAmounts amount={amount} onSelect={onCashChange} />

      {/* Numpad */}
      <Numpad value={cashTendered} onChange={onCashChange} />

      {/* Change Calculator */}
      {cashTendered > 0 && <ChangeCalculator tendered={cashTendered} due={amount} />}

      {/* Submit */}
      <Button
        className="w-full"
        size="lg"
        onClick={() => onSubmit(cashTendered)}
        disabled={!canSubmit}
      >
        Accept Cash Payment
      </Button>
    </div>
  );
}
